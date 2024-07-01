import interactions
from database import *
from sqlalchemy import text
from config import models
from interactions.ext.paginators import Page, Paginator


# all class names from this file have to be included in def below
def setup(bot):
    Inventory(bot)


class Inventory(interactions.Extension):
    # constructor
    def __init__(self, bot):
        self.bot = bot

    @interactions.slash_command(description='Zarządzanie ekwipunkiem', scopes=['917078941213261914'])
    async def inventory(self, ctx: interactions.SlashContext):
        return

    @inventory.subcommand(sub_cmd_name="list")
    @interactions.slash_option(name='country', opt_type=interactions.OptionType.STRING,
                               description='Podaj nazwę państwa lub oznacz gracza. Zostaw puste dla swojego.')
    @interactions.slash_option(name='sort',
                               opt_type=interactions.OptionType.STRING,
                               description='Sortuj ekwipunek',
                               choices=[
                                   interactions.SlashCommandChoice(name='wg nazwy', value='name'),
                                   interactions.SlashCommandChoice(name='wg ilości', value='count')
                               ])
    @interactions.slash_option(name='order',
                               opt_type=interactions.OptionType.STRING,
                               description='Rosnąco/Malejąco',
                               choices=[
                                   interactions.SlashCommandChoice(name='rosnąco', value='ASC'),
                                   interactions.SlashCommandChoice(name='malejąco', value='DESC')
                               ])
    async def list(self, ctx: interactions.SlashContext, country: str = '', sort: str = 'name', order: str = 'ASC'):

        await ctx.defer()
        connection = db.pax_engine.connect()

        if country.startswith('<@') and country.endswith('>'):  # if a ping
            # id = panstwo[2:-1]
            result = connection.execute(
                text(
                    f'SELECT country_name FROM players NATURAL JOIN countries WHERE player_id = {country[2:-1]}')).fetchone()
            if result is None:
                await ctx.send('Ten gracz nie ma przypisanego państwa.')
                connection.close()
                return
            country = result[0]
        elif country != '':
            result = connection.execute(
                text(f'SELECT country_name FROM countries WHERE country_name = "{country}"')).fetchone()
            if result is None:
                await ctx.send('Takie państwo nie istnieje.')
                connection.close()
                return
        else:
            country = connection.execute(
                text(
                    f'SELECT country_name from players NATURAL JOIN countries WHERE player_id = {ctx.author.id};')).fetchone()[
                0]

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

    @inventory.subcommand(sub_cmd_name="item")
    @interactions.slash_option(name='item', description='O jakim itemie wyświetlić informacje?',
                               opt_type=interactions.OptionType.STRING, required=True,
                               autocomplete=True)
    @interactions.slash_option(name='admin', description='Jesteś admin?.',
                               opt_type=interactions.OptionType.STRING)
    async def item(self, ctx: interactions.SlashContext, item: str, admin: str = ''):
        country_id = db.pax_engine.connect().execute(text(
            f'SELECT country_id FROM players NATURAL JOIN countries WHERE player_id = {ctx.author.id}')).fetchone()

        if admin == "admin" and ctx.author.has_permission(interactions.Permissions.ADMINISTRATOR):
            admin = True
            query = db.pax_engine.connect().execute(text(f'SELECT item_id, item_name FROM items')).fetchall()
        else:
            admin = False
            query = db.pax_engine.connect().execute(text(
                f'SELECT item_id, item_name FROM countries NATURAL JOIN inventories NATURAL JOIN items '
                f'WHERE country_id = {country_id[0]} AND NOT quantity <= 0')).fetchall()

        index = 0
        for i, row in enumerate(query):
            if str.lower(row[1]) == str.lower(item):
                index = i
        single_list = []
        for row in query:
            single_list.append(row[0])

        if admin:
            pages = []
            for item_id in single_list:
                embed = await models.build_item_embed_admin(item_id)
                pages.append(embed)

            paginator = Paginator.create_from_embeds(ctx.client, *pages)
            paginator.page_index = index
            await paginator.send(ctx=ctx)
        else:
            match len(single_list):
                case 0:
                    await ctx.send("Nie masz nic w ekwipunku!")
                case 1:
                    embed = await models.build_item_embed(ctx, self, single_list[0], country_id[0])
                    await ctx.send(embeds=embed)
                case _:
                    pages = []
                    for item_id in single_list:
                        embed = await models.build_item_embed(ctx, self, item_id, country_id[0])
                        pages.append(embed)
                    paginator = Paginator.create_from_embeds(ctx.client, *pages)
                    paginator.page_index = index
                    await paginator.send(ctx=ctx)

    @item.autocomplete("item")
    async def item_autocomplete(self, ctx: interactions.AutocompleteContext):
        items = db.pax_engine.connect().execute(text(
            f'SELECT item_name FROM players NATURAL JOIN countries NATURAL JOIN inventories NATURAL JOIN items '
            f'WHERE player_id = "{ctx.author.id}" AND quantity > 0')).fetchall()
        item = ctx.input_text
        if item == "":
            choices = [
                interactions.SlashCommandChoice(name=item_name[0], value=item_name[0])
                for item_name in items
            ]
        else:
            choices = [
                interactions.SlashCommandChoice(name=item_name[0], value=item_name[0])
                for item_name in items if str.lower(item) in str.lower(item_name[0])
            ]
        await ctx.send(choices)

    @inventory.subcommand(sub_cmd_name="give")
    @interactions.slash_option(name='country', description='a',
                               opt_type=interactions.OptionType.STRING)
    @interactions.slash_option(name='items', description='b',
                               opt_type=interactions.OptionType.STRING)
    @interactions.slash_option(name='admin', description='c',
                               opt_type=interactions.OptionType.BOOLEAN)
    async def give(self, ctx: interactions.SlashContext, country: str, items: str, admin: bool = False):
        await ctx.defer()

        connection = db.pax_engine.connect()

        if admin:
            if not ctx.author.has_permission(interactions.Permissions.ADMINISTRATOR):
                await ctx.send("You have no power here!")
                return
        else:
            author_country = connection.execute(
                text(f'SELECT country_id FROM players WHERE player_id = "{ctx.author.id}"')).fetchone()
            if author_country is None:
                await ctx.send('Nie masz przypisanego żadnego państwa!')
                connection.close()
                return

        if country.startswith('<@') and country.endswith('>'):  # if a ping
            # id = panstwo[2:-1]
            result = connection.execute(text(
                f'SELECT country_id FROM players WHERE player_id = {country[2:-1]};')).fetchone()
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

        items = items.lower().split(',')
        print(items)
        # items = items.split(',')
        for i in range(len(items)):
            items[i] = items[i].strip()
            items[i] = items[i].split(maxsplit=1)
            items[i] = [items[i][0].strip(), items[i][1].strip()]
            result = connection.execute(
                text(f'SELECT item_id FROM items WHERE LOWER(item_name) = LOWER("{items[i][1]}");')).fetchone()
            if result is None:
                await ctx.send(f'Nie istnieje przedmiot o nazwie: {items[i][0]}!')
                return

            if not admin and items[i][0][:1] in '-=':
                await ctx.send('Nie posiadasz uprawnień, by odbierać lub ustawiać wartości w ekwipunku!')
                return
            items[i].append(result[0])

        if not admin:
            result = connection.execute(
                text(f'SELECT quantity, item_id FROM inventories WHERE country_id = {author_country[0]}')).fetchall()
            player_inventory = [item for item in result]
            for item in items:
                player_has_item = False
                for jtem in player_inventory:
                    print(item[2])
                    print(jtem[1])
                    print(item[1])
                    print(jtem[0])
                    print(item)
                    print(jtem)
                    if item[2] == jtem[1] and int(item[0]) <= jtem[0]:
                        player_has_item = True
                        break
                if not player_has_item:
                    await ctx.send(f'Twoje państwo nie posiada tyle {item[0]}!')
                    connection.close()
                    return

        endqueries = []
        endmessage = ''
        # Now iterate through items and amounts and if there is something in result -> increase quantity.
        # Update. Then insert into the rest
        for item in items:
            if not admin:
                endqueries.append(
                    f'INSERT INTO inventories VALUES ({item[2]},{country},{item[0]}) '
                    f'ON DUPLICATE KEY UPDATE quantity = quantity + {item[0]};'
                )
                endmessage += f'{item[1]} {item[0]}, '
                endqueries.append(
                    f'UPDATE inventories SET quantity = quantity - {item[0]} '
                    f'WHERE item_id = {item[2]} and country_id = {author_country[0]};')
            elif admin:
                if items[0][:1] in '+-=':
                    mode = items[0][:1]
                else:
                    mode = '+'

                match mode:
                    case '+' | '-':
                        endqueries.append(
                            f'INSERT INTO inventories VALUES ({item[2]},{country},{item[0]}) '
                            f'ON DUPLICATE KEY UPDATE quantity = quantity {mode} {item[0]};')
                    case '=':
                        endqueries.append(
                            f'INSERT INTO inventories VALUES ({item[2]},{country},{item[0]}) '
                            f'ON DUPLICATE KEY UPDATE quantity = {item[0]};')
                endmessage += f'{item[1]} {item[0]}, '

        connection.rollback()
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
        await ctx.send(f'Przekazano: {endmessage[0:-2:1]} państwu {country_name}.')

        connection.close()

    ###############
    # admin debug #
    ###############

    # @inventory.subcommand(description='!ADMIN ONLY!')
    # @interactions.slash_option(name='country', description='a')
    # @interactions.slash_option(name='items', description='b')
    # async def add(self, ctx: interactions.SlashContext, country: str, items: str):
    #     if not await ctx.author.has_permissions(interactions.Permissions.ADMINISTRATOR):
    #         await ctx.send("You have no power here!")
    #         return
    #
    #     await ctx.defer()
    #
    #     connection = db.pax_engine.connect()
    #     if country.startswith('<@') and country.endswith('>'):  # if a ping
    #         # id = panstwo[2:-1]
    #         result = connection.execute(text(
    #             f'SELECT country_id FROM players NATURAL JOIN countries WHERE player_id = {country[2:-1]};')).fetchone()
    #         if result is None:
    #             await ctx.send('Ten gracz nie ma przypisanego państwa.')
    #             connection.close()
    #             return
    #         country = result[0]
    #     else:
    #         result = connection.execute(
    #             text(f'SELECT country_id FROM countries WHERE LOWER(country_name) = LOWER("{country}");')).fetchone()
    #         if result is None:
    #             await ctx.send(f'Państwo "{country}" nie istnieje.')
    #             connection.close()
    #             return
    #         country = result[0]
    #
    #     items = items.lower()
    #     items = items.split(',')
    #     for i in range(len(items)):
    #         items[i] = items[i].strip()
    #         items[i] = items[i].split(' ')
    #         result = connection.execute(
    #             text(f'SELECT item_id FROM items WHERE LOWER(item_name) = LOWER("{items[i][0]}");')).fetchone()
    #         if result is None:
    #             await ctx.send(f'Nie istnieje przedmiot o nazwie: {items[i][0]}!')
    #             return
    #         items[i].append(result[0])
    #
    #     # for i in range(len(items)):
    #     #     items[i] = items[i].split()
    #     endqueries = []
    #     endmessage = ''
    #     result = connection.execute(
    #         text(f'SELECT DISTINCT LOWER(item_name), quantity, item_id FROM inventories '
    #              f'NATURAL JOIN countries NATURAL JOIN items '
    #              f'WHERE country_id = {country};')).fetchall()
    #     # Now iterate through items and amounts and if there is something in result -> increase quantity.
    #     # Update. Then insert into the rest
    #     for item in items:
    #         found = False
    #         for row in result:
    #             if item[0] == row[0]:
    #                 found = True
    #                 endqueries.append(
    #                     f'UPDATE inventories SET quantity = quantity + {item[1]} '
    #                     f'WHERE item_id = {item[2]} and country_id = {country};')
    #                 endmessage += f'{item[1]} {item[0]}, '
    #                 break
    #         if not found:
    #             endqueries.append(
    #                 f'INSERT INTO inventories VALUES ({item[2]},{country},{item[1]});')
    #     connection.rollback()
    #
    #     connection.begin()
    #     for query in endqueries:
    #         try:
    #             connection.execute(text(query))
    #         except:
    #             connection.rollback()
    #             await ctx.send(
    #                 'Ojoj! Coś poszło nie tak. Spróbuj ponownie później lub skontaktuj się z administratorem.')
    #             return
    #     connection.commit()
    #
    #     country_name = connection.execute(
    #         text(f'SELECT country_name FROM countries WHERE country_id = {country};')).fetchone()[0]
    #     await ctx.send(f'Przekazano: {endmessage[0:-2:1]} państwu {country_name}.')
    #
    #     connection.close()
    #     return
