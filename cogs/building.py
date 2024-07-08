import interactions
from database import *
from sqlalchemy import text
from config import models
from interactions.ext.paginators import Paginator
import json

with open("./config/config.json") as f:
    configure = json.load(f)


# all class names from this file have to be included in def below
def setup(bot):
    Building(bot)


class Building(interactions.Extension):
    # constructor
    def __init__(self, bot):
        self.bot = bot

    @interactions.slash_command(description='Zarządzanie budynkami', scopes=[configure['GUILD']])
    async def building(self, ctx: interactions.SlashContext):
        pass

    @building.subcommand(sub_cmd_description='Lista twoich zbudowanych budynków')
    @interactions.slash_option(name='province', description='#Id lub nazwa prowincji', required=True,
                               opt_type=interactions.OptionType.STRING)
    @interactions.slash_option(name='country', description='Nazwa państwa lub ping',
                               opt_type=interactions.OptionType.STRING)
    @interactions.slash_option(name='admin', description='Admin?',
                               opt_type=interactions.OptionType.BOOLEAN)
    async def list(self, ctx: interactions.SlashContext, province: str = '', country: str = '', admin: bool = False):
        is_admin = admin and ctx.author.has_permission(interactions.Permissions.ADMINISTRATOR)

        return

    @building.subcommand(sub_cmd_description='Lista twoich szablonów budynków')
    @interactions.slash_option(name='tryb', description='W jakim trybie wyświetlić informacje?',
                               opt_type=interactions.OptionType.STRING, required=True,
                               choices=[interactions.SlashCommandChoice(name="Dokładny", value="pages"),
                                        interactions.SlashCommandChoice(name="Prosty", value="list")])
    @interactions.slash_option(name='admin', opt_type=interactions.OptionType.STRING,
                               description='Jesteś admin?')
    async def templates(self, ctx: interactions.SlashContext, tryb: str = '', admin: str = ''):
        await ctx.defer()
        connection = db.pax_engine.connect()

        if admin != '' and ctx.author.has_permission(interactions.Permissions.ADMINISTRATOR):
            if admin == "admin":
                country_id = '%'
            elif admin.startswith('<@') and admin.endswith('>'):  # if a ping
                country_id = connection.execute(text(
                    f'SELECT country_id FROM players NATURAL JOIN countries '
                    f'WHERE player_id = {admin[2:-1]}')).fetchone()[0]
            else:
                country_id = connection.execute(text(
                    f'SELECT country_id FROM players NATURAL JOIN countries WHERE country_name = "{admin}"'
                )).fetchone()[0]
        else:
            country_id = connection.execute(text(
                f'SELECT country_id FROM countries NATURAL JOIN players WHERE player_id = "{ctx.author.id}"'
            )).fetchone()[0]
        pages = await models.bt_list(self, country_id=country_id)

        if len(pages) == 1:
            await ctx.send(embed=pages[0])
        else:
            paginator = Paginator.create_from_embeds(ctx.client, *pages)
            await paginator.send(ctx=ctx)

        connection.close()
        return

    @building.subcommand(sub_cmd_description='Budowanie budynków')
    @interactions.slash_option(name='building', description='Nazwa budynku który chcesz zbudować',
                               opt_type=interactions.OptionType.STRING, required=True)
    @interactions.slash_option(name='province', description='W jakiej prowincji chcesz zbudować budynek?',
                               opt_type=interactions.OptionType.STRING, required=True)
    @interactions.slash_option(name='admin', description='Jesteś admin?', required=False,
                               opt_type=interactions.OptionType.BOOLEAN)
    async def build(self, ctx: interactions.SlashContext, building: str, province: str, admin: bool = False):
        connection = db.pax_engine.connect()
        is_admin = admin and ctx.author.has_permission(interactions.Permissions.ADMINISTRATOR)


        country_id = connection.execute(
            text(
                f'SELECT country_id from players NATURAL JOIN countries WHERE player_id = {ctx.author.id};')).fetchone()[
            0]
        if country_id is None and not is_admin:
            await ctx.send(embed=interactions.Embed(description=f'Nie posiadasz państwa!'))
            return
        if is_admin:
            country_id = '%'

        if province.startswith('#'):
            query = connection.execute(text(
                f'SELECT province_id, province_name FROM provinces WHERE province_id = "{province[1:]}"'
            )).fetchone()
            if query is None and not is_admin:
                await ctx.send(embed=interactions.Embed(description=f'Nie istnieje prowincja o ID **{province}**!'))
                return
            province_id, province_name = query
        else:
            query = connection.execute(text(
                f'SELECT province_id, province_name FROM provinces WHERE province_name = "{province}"'
            )).fetchone()
            if query is None and not is_admin:
                await ctx.send(embed=interactions.Embed(description=f'Nie istnieje prowincja o nazwie **{province}**!'))
                return
            province_id, province_name = query

        number_of_buildings, max_buildings, province_owner, province_controller = connection.execute(text(
            f"""
                SELECT 
                  COUNT(*), 
                  province_building_limit,
                  country_id,
                  controller_id
                FROM 
                  provinces NATURAL 
                  JOIN structures NATURAL 
                  JOIN province_levels 
                WHERE 
                  province_id = {province_id};
                """
        )).fetchone()
        print(f'country_id = {country_id}')
        print(f'owner = {province_owner}')
        print(f'controller = {province_controller}')
        if (province_owner != country_id) and (not is_admin):
            await ctx.send(embed=interactions.Embed(description=f'Prowincja **{province_name} (#{province_id})**'
                                                                f' nie jest w pełni kontrolowana przez twoje państwo!'))
            return

        costs = {}
        building = building.strip().split(',')  # ['2 Tartak', '2 Kopalnia']
        for i, b in enumerate(building):
            b = str(b).strip()
            print(b[0])
            if not str.isdigit(b[0]):
                print('added')
                b = '1 ' + b
            building[i] = b.split()  # [['2', 'Tartak'], ['2', 'Kopalnia']]
            print(building[i] is not list)
            print(len(building[i]))
            print(type(building[i]))
            if building[i] is str or len(building[i]) < 2:
                building[i].insert(0, '1')
            if len(building[i]) != 2:
                await ctx.send(embed=interactions.Embed(description=f'Argument ma złą składnię! **{building[i]}**!'))
                return

            query = connection.execute(text(
                f"""
                SELECT 
                  b.building_id, 
                  b.building_name,
                  b.building_emoji,
                  b.building_id,
                  bc.item_id,
                  bc.item_quantity
                FROM 
                  country_buildings cb NATURAL
                  JOIN buildings b NATURAL 
                  JOIN buildings_cost bc 
                WHERE 
                  b.building_name = '{building[i][1]}' 
                  AND (cb.country_id LIKE '{country_id}' OR cb.country_id = 255);
                """
            )).fetchall()

            if query is None:
                await ctx.send(
                    embed=interactions.Embed(description=f'Nie masz szablonu bundyku o nazwie **{building[i][1]}**!'))
                return

            building[i].append(query[0][2])  # [['1', 'Tartak', ':tartak:], ['2', 'Kopalnia', ':kopalnia:]]
            building[i].append(query[0][3])  # [['1', 'Tartak', ':tartak:, 1], ['2', 'Kopalnia', ':kopalnia:, 3]]

            for cost in query:
                if cost[4] not in costs:
                    costs[cost[4]] = cost[5] * int(building[i][0])  # "2": 200
                else:
                    costs[cost[4]] += cost[5] * int(building[i][0])  # "2": 400
            print(building[i][1])
            print(query)

        # ENTER ADMIN MODE
        if is_admin:
            spawned_buildings = ''
            for b in building:
                print(b)
                print(b[0])
                print(type(b[0]))
                spawned_buildings = spawned_buildings + f', {b[0]} {b[2]} **{b[1]}**'
                connection.execute(text(
                    f"""
                    INSERT INTO structures (
                      province_id, building_id, quantity
                    ) 
                    VALUES 
                      ({province_id}, {b[3]}, {int(b[0])}) ON DUPLICATE KEY 
                    UPDATE 
                      quantity = quantity + 1
                    """
                ))
            connection.commit()
            print(spawned_buildings)
            await ctx.send(embeds=interactions.Embed(title=f'Zespawnowano budynki w prowincji **{province_name} (#{province_id})!**',
                                                     description=f'{spawned_buildings[2:]}'))
            return

        print(costs)  # {2: 1500, 4: 40, 5: 60}

        if (number_of_buildings + sum(
                [int(i) for i in list(zip(*building))[0]])) > max_buildings:  # buildings + new_buildings > max
            await ctx.send(embed=interactions.Embed(description=f'W prowincji **{province_name} (#{province_id})**'
                                                                f' nie ma tyle miejsc na budynki!\n'
                                                                f'`{number_of_buildings} +'
                                                                f' {sum([int(i) for i in list(zip(*building))[0]])} > {max_buildings}`'))
            return

        keys = ''
        for key in costs:
            keys = keys + f', {key}'  # '2, 4, 5'

        inventory = connection.execute(text(
            f"SELECT it.item_id, inv.quantity, it.item_emoji, it.item_name "
            f"FROM inventories inv NATURAL JOIN items it "
            f"WHERE it.item_id IN ({keys[2:]}) AND inv.country_id = '{country_id}'"
        )).fetchall()  # [[2, 1000.00], [4, 190.00], [4, 0.00]]

        for item in inventory:
            if item[1] < costs[item[0]]: # 1000.00 < 1500
                resources_required = ''
                for jtem in inventory:
                    if jtem[1] > costs[jtem[0]]:
                        resources_required = resources_required + f', {jtem[2]} **{jtem[3]} [{jtem[1]}/{costs[jtem[0]]}]**'
                    else:
                        resources_required = resources_required + f', {jtem[2]} {jtem[3]} [{jtem[1]}/{costs[jtem[0]]}]'
                await ctx.send(
                    embed=interactions.Embed(description=f'Nie masz wystarczająco zasobów żeby wybudować budynki!\n'
                                                         f'{resources_required[2:]}'))
                return

        connection.close()
        return
    