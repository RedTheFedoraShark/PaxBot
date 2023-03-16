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
    async def inventory(self, ctx: interactions.CommandContext):
        return

    @inventory.subcommand(description='Zobacz ekwipunek')
    @interactions.option(name='country', description='Podaj nazwę państwa lub oznacz gracza')
    @interactions.option(name='sort', description='Sortuj ekwipunek',
                         choices=[
                             interactions.Choice(name='wg nazwy', value='name'),
                             interactions.Choice(name='wg ilości', value='count')
                         ])
    @interactions.option(name='order', description='Rosnąco/Malejąco',
                         choices=[
                             interactions.Choice(name='rosnąco', value='ASC'),
                             interactions.Choice(name='malejąco', value='DESC')
                         ])
    async def list(self, ctx: interactions.CommandContext, country: str='', sort: str='name', order: str='ASC'):

        await ctx.defer()
        connection = db.pax_engine.connect()

        if country.startswith('<@') and country.endswith('>'): # if a ping
            # id = panstwo[2:-1]
            result = connection.execute(
                text(f'SELECT country_name FROM players NATURAL JOIN countries WHERE player_id = {country[2:-1]}')).fetchone()
            if result is None:
                await ctx.send('Ten gracz nie ma przypisanego państwa.')
                connection.close()
                return
            country = result[0]
        else:
            result = connection.execute(text(f'SELECT country_name FROM countries WHERE country_name = "{country}"')).fetchone()
            if result is None:
                await ctx.send('Takie państwo nie istnieje.')
                connection.close()
                return

        result = connection.execute(
            text(f'SELECT DISTINCT item_name, quantity, item_emoji '
                 f'FROM inventories NATURAL JOIN countries NATURAL JOIN items '
                 f'WHERE LOWER(country_name) = LOWER("{country}")')).fetchall()

        embed = interactions.Embed(
            title=f'Magazyny państwa {country}',
            footer=interactions.EmbedFooter(text='This is a footer.'),
        )
        items = ""
        quantities = ""

        for item, quantity, emoji in result:
            if quantity == 0:
                continue
            items += f'{item}\n'
            quantities += str(quantity) + '\n'

        embed.add_field(name='Zasób', value=items, inline=True)
        embed.add_field(name='Ilość', value=quantities, inline=True)
        await ctx.send(embeds=embed)

        connection.close()
        return

    @inventory.subcommand(description='Zaproponuj coś innemu graczu.')
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

    @inventory.subcommand(description='Przekaż coś innemu graczu.')
    @interactions.option(name='country', description='a')
    @interactions.option(name='items', description='b')
    async def give(self, ctx: interactions.CommandContext, country: str, items: str):
        await ctx.defer()

        connection = db.pax_engine.connect()

        author_country = connection.execute(
            text(f'SELECT country_id FROM players WHERE player_id = "{ctx.author.id}"')).fetchone()
        if author_country is None:
            await ctx.send('Nie masz przypisanego żadnego państwa!')
            connection.close()
            return

        if country.startswith('<@') and country.endswith('>'):  # if a ping
            # id = panstwo[2:-1]
            result = connection.execute(text(
                f'SELECT country_id FROM players NATURAL JOIN countries WHERE player_id = {country[2:-1]};')).fetchone()
            if result is None:
                await ctx.send('Ten gracz nie ma przypisanego państwa.')
                connection.close()
                return
            country = result[0]
        else:
            result = connection.execute(
                text(f'SELECT country_id FROM countries WHERE LOWER(country_name) = LOWER("{country}");')).fetchone()
            if result is None:
                await ctx.send(f'Państwo "{country}" nie istnieje.')
                connection.close()
                return
            country = result[0]

        items = items.lower()
        items = items.split(',')
        for i in range(len(items)):
            items[i] = items[i].strip()
            items[i] = items[i].split(' ')
            result = connection.execute(
                text(f'SELECT item_id FROM items WHERE LOWER(item_name) = LOWER("{items[i][0]}");')).fetchone()
            if result is None:
                await ctx.send(f'Nie istnieje przedmiot o nazwie: {items[i][0]}!')
                return
            items[i].append(result[0])

        result = connection.execute(
            text(f'SELECT quantity, item_id FROM inventories WHERE country_id = {author_country}')).fetchall()
        player_inventory = [item for item in result]
        for item in items:
            player_has_item = False
            for jtem in player_inventory:
                if item[2] == jtem[1] and item[1] <= jtem[0]:
                    player_has_item = True
                    break
            if not player_has_item:
                await ctx.send(f'Twoje państwo nie posiada tyle {item[0]}!')
                connection.close()
                return

        endqueries = []
        endmessage = ''
        result = connection.execute(
            text(f'SELECT DISTINCT LOWER(item_name), quantity, item_id FROM inventories '
                 f'NATURAL JOIN countries NATURAL JOIN items '
                 f'WHERE country_id = {country};')).fetchall()
        # Now iterate through items and amounts and if there is something in result -> increase quantity.
        # Update. Then insert into the rest
        for item in items:
            found = False
            for row in result:
                if item[0] == row[0]:
                    found = True
                    endqueries.append(
                        f'UPDATE inventories SET quantity = quantity + {item[1]} '
                        f'WHERE item_id = {item[2]} and country_id = {country};')
                    endqueries.append(
                        f'UPDATE inventories SET quantity = quantity - {item[1]} '
                        f'WHERE item_id = {item[2]} and country_id = {author_country};')
                    endmessage += f'{item[1]} {item[0]}, '
                    break
            if not found:
                endqueries.append(f'INSERT INTO inventories VALUES ({item[2]},{country},{item[1]});')
        connection.rollback()
        print(endqueries)
        connection.begin()
        for query in endqueries:
            try:
                connection.execute(text(query))
            except:
                connection.rollback()
                await ctx.send(
                    "Ojoj! Coś poszło nie tak. Spróbuj ponownie później lub skontaktuj się z administratorem.")
                return
        connection.commit()

        country_name = connection.execute(
            text(f'SELECT country_name FROM countries WHERE country_id = {country};')).fetchone()[0]
        await ctx.send(f'Przekazano {endmessage[:-1]} państwu {country_name}.')

        connection.close()

    ###############
    # admin debug #
    ###############

    @inventory.subcommand(description='!ADMIN ONLY!')
    @interactions.option(name='country', description='a')
    @interactions.option(name='items', description='b')
    async def add(self, ctx: interactions.CommandContext, country: str, items: str):
        if not await ctx.author.has_permissions(interactions.Permissions.ADMINISTRATOR):
            await ctx.send("You have no power here!")
            return

        await ctx.defer()

        connection = db.pax_engine.connect()
        if country.startswith('<@') and country.endswith('>'):  # if a ping
            # id = panstwo[2:-1]
            result = connection.execute(text(
                f'SELECT country_id FROM players NATURAL JOIN countries WHERE player_id = {country[2:-1]};')).fetchone()
            if result is None:
                await ctx.send('Ten gracz nie ma przypisanego państwa.')
                connection.close()
                return
            country = result[0]
        else:
            result = connection.execute(
                text(f'SELECT country_id FROM countries WHERE LOWER(country_name) = LOWER("{country}");')).fetchone()
            if result is None:
                await ctx.send(f'Państwo "{country}" nie istnieje.')
                connection.close()
                return
            country = result[0]

        items = items.lower()
        items = items.split(',')
        for i in range(len(items)):
            items[i] = items[i].strip()
            items[i] = items[i].split(' ')
            result = connection.execute(
                text(f'SELECT item_id FROM items WHERE LOWER(item_name) = LOWER("{items[i][0]}");')).fetchone()
            if result is None:
                await ctx.send(f'Nie istnieje przedmiot o nazwie: {items[i][0]}!')
                return
            items[i].append(result[0])

        # for i in range(len(items)):
        #     items[i] = items[i].split()
        endqueries = []
        endmessage = ''
        result = connection.execute(
            text(f'SELECT DISTINCT LOWER(item_name), quantity, item_id FROM inventories '
                 f'NATURAL JOIN countries NATURAL JOIN items '
                 f'WHERE country_id = {country};')).fetchall()
        # Now iterate through items and amounts and if there is something in result -> increase quantity.
        # Update. Then insert into the rest
        for item in items:
            found = False
            for row in result:
                if item[0] == row[0]:
                    found = True
                    endqueries.append(
                        f'UPDATE inventories SET quantity = quantity + {item[1]} '
                        f'WHERE item_id = {item[2]} and country_id = {country};')
                    endmessage += f'{item[1]} {item[0]}, '
                    break
            if not found:
                endqueries.append(
                    f'INSERT INTO inventories VALUES ({item[2]},{country},{item[1]});')
        connection.rollback()
        print(endqueries)
        connection.begin()
        for query in endqueries:
            try:
                connection.execute(text(query))
            except:
                connection.rollback()
                await ctx.send(
                    'Ojoj! Coś poszło nie tak. Spróbuj ponownie później lub skontaktuj się z administratorem.')
                return
        connection.commit()

        country_name = connection.execute(
            text(f'SELECT country_name FROM countries WHERE country_id = {country};')).fetchone()[0]
        await ctx.send(f'Przekazano {endmessage[:-1]} państwu {country_name}.')

        connection.close()
        return
