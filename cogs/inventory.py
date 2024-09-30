import interactions
from database import *
from sqlalchemy import text
from config import models
from interactions.ext.paginators import Paginator
import json

with open("./config/config.json") as f:
    configure = json.load(f)


def setup(bot):
    Inventory(bot)


class Inventory(interactions.Extension):
    # constructor
    def __init__(self, bot):
        self.bot = bot

    @interactions.slash_command(description='Zarządzanie ekwipunkiem', scopes=[configure['GUILD']])
    async def inventory(self, ctx: interactions.SlashContext):
        return

    @inventory.subcommand(sub_cmd_name="list")
    @interactions.slash_option(name='tryb',
                               description='W jakim trybie wyświetlić informacje? (NIE DZIAŁA - ZAWSZE PROSTY)',
                               opt_type=interactions.OptionType.STRING, required=True,
                               choices=[interactions.SlashCommandChoice(name="Dokładny", value="pages"),
                                        interactions.SlashCommandChoice(name="Prosty", value="list")])
    @interactions.slash_option(name='admin', opt_type=interactions.OptionType.STRING,
                               description='Admin?')
    async def list(self, ctx: interactions.SlashContext, tryb: str = '', admin: str = ''):
        await ctx.defer()
        connection = db.pax_engine.connect()

        if admin != '' and ctx.author.has_permission(interactions.Permissions.ADMINISTRATOR):
            if admin.startswith('<@') and admin.endswith('>'):  # if a ping
                country_id = connection.execute(text(
                    f'SELECT country_id FROM players NATURAL JOIN countries '
                    f'WHERE player_id = {admin[2:-1]}')).fetchone()
                if not country_id:
                    await ctx.send(embed=interactions.Embed(description=f'Gracz **{admin}** nie ma państwa!'))
                    connection.close()
                    return
                country_id = country_id[0]
            else:
                country_id = connection.execute(text(
                    f'SELECT country_id FROM players NATURAL JOIN countries WHERE country_name = "{admin}"'
                )).fetchone()
                if not country_id:
                    await ctx.send(embed=interactions.Embed(description=f'Państwo **{admin}** nie istnieje!'))
                    connection.close()
                    return
                country_id = country_id[0]
        else:
            country_id = connection.execute(text(
                f'SELECT country_id FROM countries NATURAL JOIN players WHERE player_id = "{ctx.author.id}"'
            )).fetchone()
            if not country_id:
                await ctx.send(embed=interactions.Embed(description=f'Nie masz przypisanego państwa!'))
                connection.close()
                return
            country_id = country_id[0]

        pages = await models.b_inventory_list(self, country_id=country_id)

        if len(pages) == 1:
            await ctx.send(embed=pages[0])
        else:
            paginator = Paginator.create_from_embeds(ctx.client, *pages)
            await paginator.send(ctx=ctx)

        connection.close()
        return

    @inventory.subcommand(sub_cmd_name="give")
    @interactions.slash_option(name='kraj', description='Wpisz dokładną nazwę kraju lub zpinguj gracza do którego '
                                                        'masz zasięg.',
                               opt_type=interactions.OptionType.STRING, required=True, autocomplete=True)
    @interactions.slash_option(name='itemy', description='ilość nazwa_itemu1, ilość nazwa_itemu2',
                               opt_type=interactions.OptionType.STRING, required=True)
    @interactions.slash_option(name='admin', description='Admin?',
                               opt_type=interactions.OptionType.BOOLEAN)
    async def give(self, ctx: interactions.SlashContext, kraj: str, itemy: str, admin: bool = False):
        await ctx.defer()

        country = kraj
        items = itemy
        connection = db.pax_engine.connect()

        if country.startswith('<@') and country.endswith('>'):  # If a ping
            q = connection.execute(text(
                f'SELECT country_id FROM players WHERE player_id = {country[2:-1]};')).fetchone()
            if q is None:
                await ctx.send(embed=interactions.Embed(description=f'Gracz **{country}** nie ma państwa!'))
                connection.close()
                return
            country = q[0]
        else:
            q = connection.execute(
                text(f'SELECT country_id FROM countries WHERE LOWER(country_name) = LOWER("{country}");')).fetchone()
            if q is None:
                await ctx.send(embed=interactions.Embed(description=f'Państwo **{country}** nie istnieje!'))
                connection.close()
                return
            country = q[0]

        if admin:
            if not ctx.author.has_permission(interactions.Permissions.ADMINISTRATOR):
                await ctx.send(embed=interactions.Embed(description=f'You have no power here!'))
                return
        else:
            author_country = connection.execute(
                text(f'SELECT country_id FROM players WHERE player_id = "{ctx.author.id}"')).fetchone()
            if author_country is None:
                await ctx.send(embed=interactions.Embed(description=f'Nie masz przypisanego państwa!'))
                connection.close()
                return

        costs = {}
        items = items.strip().split(',')  # ['2 Drewno', '-2 Talary']

        # items = items.split(',')
        for i, it in enumerate(items):
            items[i] = items[i].strip().split()  # [['+2', 'Drewno'], ['-2', 'Talary']]
            if str.isdigit(items[i][0]):
                items[i][0] = '+' + items[i][0]
            if not items[i][0] in ['+', '-', '=', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                return 0
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
                print(items)
                print(items[0][0])
                if items[0][0] in '+-=':
                    mode = items[0][0]
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

    @give.autocomplete('kraj')
    async def item_autocomplete(self, ctx: interactions.AutocompleteContext):
        connection = db.pax_engine.connect()
        country_id = connection.execute(text(
            f'SELECT country_id FROM players WHERE player_id = {ctx.author.id}'
        )).fetchone()
        connection.close()
        if not country_id:
            await ctx.send([interactions.SlashCommandChoice(name='Nie masz przypisanego państwa!',
                                                            value='Nie masz przypisanego państwa!')])
            return
        countries = models.get_trade_range(country_id[0])['country_name'].tolist()

        country = ctx.input_text
        if country == '':
            del countries[24:]
            choices = [
                interactions.SlashCommandChoice(name=c, value=c)
                for c in countries
            ]
        else:
            del countries[24:]
            choices = [
                interactions.SlashCommandChoice(name=c, value=c)
                for c in countries if str.lower(country) in c
            ]
        await ctx.send(choices)
        return
