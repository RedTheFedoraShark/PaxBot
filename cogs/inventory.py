import interactions
from database import *
from sqlalchemy import text

# all class names from this file have to be included in def below
def setup(bot):
    Inventory(bot)


class Inventory(interactions.Extension):
    # constructor
    def __init__(self, bot):
        self.bot = bot

    @interactions.extension_command(description='Zarządzanie ekwipunkiem')
    async def ekwipunek(self, ctx: interactions.CommandContext):
        return

    @ekwipunek.subcommand(description='Zobacz ekwipunek')
    @interactions.option(name='panstwo', description='Podaj nazwę państwa lub oznacz gracza')
    @interactions.option(name='sortuj', description='Sortuj ekwipunek',
                         choices=[
                             interactions.Choice(name='wg nazwy', value='name'),
                             interactions.Choice(name='wg ilości', value='count')
                         ])
    @interactions.option(name='porzadek', description='Rosnąco/Malejąco',
                         choices=[
                             interactions.Choice(name='rosnąco', value='ASC'),
                             interactions.Choice(name='malejąco', value='DESC')
                         ])
    async def lista(self, ctx: interactions.CommandContext, panstwo: str='', sort: str='name', order: str='ASC'):
        await ctx.defer()

        connection = db.pax_engine.connect()
        if panstwo.startswith('<@') and panstwo.endswith('>'): # if a ping
            # id = panstwo[2:-1]
            result = connection.execute(text(f'SELECT country_name FROM players NATURAL JOIN countries WHERE player_id = {panstwo[2:-1]}')).fetchone()
            if result is None:
                await ctx.send('Ten gracz nie ma przypisanego państwa.')
                connection.close()
                return
            panstwo = result[0]
        else:
            result = connection.execute(text(f'SELECT country_name FROM countries WHERE country_name = "{panstwo}"')).fetchone()
            if result is None:
                await ctx.send('Takie państwo nie istnieje.')
                connection.close()
                return

        result = connection.execute(text(f'SELECT DISTINCT item_name, quantity FROM inventories NATURAL JOIN countries NATURAL JOIN items WHERE LOWER(country_name) = LOWER("{panstwo}")')).fetchall()
        await ctx.send(f'a {result}')

        connection.close()
        return

    @ekwipunek.subcommand(description='Przekaż coś innemu graczu.')
    async def daj(self, ctx: interactions.CommandContext):
        pass

    @ekwipunek.subcommand(description='Zaproponuj coś innemu graczu.')
    @interactions.option(description='Jaką akcję chcesz wykonać?',
                         choices=[
                            interactions.Choice(name='dodaj', value='add'),
                            interactions.Choice(name='zabierz', value='rem'),
                            interactions.Choice(name='akceptuj', value='acc'),
                            interactions.Choice(name='odrzuć', value='ref')
                         ])
    @interactions.option(description='a')
    async def handel(self, ctx: interactions.CommandContext, action: str, temp: str):
        # get if there is an existing trade between these players
        match action:
            case "add":
                # if there is no, start a trade and add this to it
                pass
            case "rem":
                # if there is no trade, throw error
                pass
            case "acc":
                # if there is no trade, throw error
                # if both side accepted, proceed to give
                # if only one side accepted, lock the accepted side
                pass
            case "ref":
                # if there is no trade, throw error
                # if
                pass
            case _:
                pass

    @ekwipunek.subcommand(description='!ADMIN ONLY!')
    @interactions.option(name='country', description='a')
    @interactions.option(name='item', description='b')
    @interactions.option(name='amount', description='c')
    async def add(self, ctx: interactions.CommandContext, user: str, country: str):
        if not ctx.author.has_permissions(interactions.Permissions.ADMINISTRATOR):
            await ctx.send("You have no power here!")
            return

        await ctx.defer()

        connection = db.pax_engine.connect()
        if country.startswith('<@') and country.endswith('>'):  # if a ping
            # id = panstwo[2:-1]
            result = connection.execute(text(
                f'SELECT country_name FROM players NATURAL JOIN countries WHERE player_id = {country[2:-1]}')).fetchone()
            if result is None:
                await ctx.send('Ten gracz nie ma przypisanego państwa.')
                connection.close()
                return
            country = result[0]
        else:
            result = connection.execute(
                text(f'SELECT country_name FROM countries WHERE country_name = "{country}"')).fetchone()
            if result is None:
                await ctx.send('Takie państwo nie istnieje.')
                connection.close()
                return


        await ctx.send(f'a {result}')

        connection.close()
        return
