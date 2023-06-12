import interactions
from database import *
from sqlalchemy import text
from config import models

# all class names from this file have to be included in def below
def setup(bot):
    Template(bot)


class Template(interactions.Extension):
    # constructor
    def __init__(self, bot):
        self.bot = bot

    @interactions.extension_command(
        description='Lista twoich szablonów budynków'
    )
    async def templates(self, ctx: interactions.CommandContext):
        await ctx.defer()
        connection = db.pax_engine.connect()

        country = connection.execute(text(f'SELECT country_id FROM players WHERE player_id = {ctx.author.id};')).fetchone()[0]
        if country is None:
            await ctx.send('Nie masz przypisanego państwa!')
            return

        buildings = connection.execute(
            text(f'SELECT building_id, building_name, building_desc, building_emoji '
                 f'FROM country_buildings NATURAL JOIN buildings '
                 f'WHERE country_id = "{country}" ORDER BY building_id DESC;')).fetchall()

        the_list = '```ani\n'
        for building in buildings:
            incomes = connection.execute(
                text(f'SELECT item_name, item_quantity '
                     f'FROM buildings_production WHERE building_id = {building[0]}')).fetchall()
            building.append([income for income in incomes])
            the_list += f'{building[3]} {building[1]}\n\t{building[2]}'
        the_list += '```'
        connection.close()
        return
