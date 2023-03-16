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
            # id = panstwo[2:-1]
            result = connection.execute(
                text(f'SELECT country_name, country_id FROM players NATURAL JOIN countries WHERE player_id = {country[2:-1]}')).fetchone()
            if result is None:
                await ctx.send('Ten gracz nie ma przypisanego państwa.')
                connection.close()
                return
            country = result[0]
        else:
            result = connection.execute(
                text(f'SELECT country_name, country_id FROM countries WHERE country_name = "{country}"')).fetchone()
            if result is None:
                await ctx.send('Takie państwo nie istnieje.')
                connection.close()
                return


        connection.close()
        return
