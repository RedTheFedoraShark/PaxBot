import interactions
from database import *
from sqlalchemy import text

# all class names from this file have to be included in def below
def setup(bot):
    Province(bot)


class Province(interactions.Extension):
    # constructor
    def __init__(self, bot):
        self.bot = bot

    @interactions.extension_command(description='dummy')
    async def province(self, ctx: interactions.CommandContext):
        return

    @province.subcommand(description='')
    @province.option(name='country', description='Podaj nazwę państwa lub oznacz gracza')
    async def list(self, ctx: interactions.CommandContext(), country: str):

        await ctx.defer()
        connection = db.pax_engine.connect()
        if country.startswith('<@') and country.endswith('>'): # if a ping
            result = connection.execute(
                text(f'SELECT country_name, country_id FROM players NATURAL JOIN countries WHERE player_id = {country[2:-1]}')).fetchone()
            if result is None:
                await ctx.send('Ten gracz nie ma przypisanego państwa.')
                connection.close()
                return
            country = result[1]
        elif country != '':
            result = connection.execute(
                text(f'SELECT country_name, country_id FROM countries WHERE country_name = "{country}"')).fetchone()
            if result is None:
                await ctx.send('Takie państwo nie istnieje.')
                connection.close()
                return
            country = result[1]
        else:
            country = connection.execute(
                text(f'SELECT country_name, country_id from players NATURAL JOIN countries WHERE player_id = {ctx.author.id};')).fetchone()[1]

        result = connection.execute(
            text(f'SELECT province_id, province_name, region_name, terrain_name, good_name, '
                 f'religion_name, country_name, province_pops, province_pops_used, province_autonomy '
                 f'FROM provinces '
                 f'NATURAL JOIN terrains '
                 f'NATURAL JOIN goods '
                 f'NATURAL JOIN regions '
                 f'NATURAL JOIN religions'
                 f'NATURAL JOIN countries'
                 f'WHERE country_id = 1'))

        connection.close()
        return

    @province.subcommand(description='a')
    @interactions.option(name='proivnce', description='Nazwa lub id prowincji.')
    async def details(self, ctx: interactions.CommandContext, province: str):

        self.bot.defer()
        connection = db.pax_engine.connect()



        result = connection.execute(
            text(f'SELECT province_id, province_name, region_name, terrain_name, good_name, '
                 f'religion_name, country_name, province_pops, province_pops_used, province_autonomy '
                 f'FROM provinces '
                 f'NATURAL JOIN terrains '
                 f'NATURAL JOIN goods '
                 f'NATURAL JOIN regions '
                 f'NATURAL JOIN religions'
                 f'NATURAL JOIN countries'
                 f'WHERE country_id = 1'))


        connection.close()
        return

    @province.subcommand(description='a')
    async def give(self, ctx: interactions.CommandContext):
        pass
