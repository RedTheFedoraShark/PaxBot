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
    @interactions.slash_option(name='tryb', description='W jakim trybie wyświetlić informacje? (NIE DZIAŁA - ZAWSZE PROSTY)',
                               opt_type=interactions.OptionType.STRING, required=True,
                               choices=[interactions.SlashCommandChoice(name="Dokładny", value="pages"),
                                        interactions.SlashCommandChoice(name="Prosty", value="list")])
    @interactions.slash_option(name='admin', description='Admin?',
                               opt_type=interactions.OptionType.STRING)
    async def list(self, ctx: interactions.SlashContext, tryb: str = '', admin: str = ''):
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

        pages = await models.b_building_list(self, country_id=country_id)
        for i, page in enumerate(pages):
            pages[i].description = page.description.replace('\n*[', ' *[')  # Little hack to adjust the message

        if len(pages) == 1:
            await ctx.send(embed=pages[0])
        else:
            paginator = Paginator.create_from_embeds(ctx.client, *pages)
            await paginator.send(ctx=ctx)

        connection.close()
        return

    @building.subcommand(sub_cmd_description='Lista twoich szablonów budynków')
    @interactions.slash_option(name='tryb', description='W jakim trybie wyświetlić informacje? (NIE DZIAŁA - ZAWSZE PROSTY)',
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
        pages = await models.b_building_templates(self, country_id=country_id)

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
            await ctx.send(embed=interactions.Embed(description=f'Nie masz przypisanego państwa!'))
            connection.close()
            return
        if is_admin:
            country_id = '%'

        if province.startswith('#'):
            query = connection.execute(text(
                f'SELECT province_id, province_name FROM provinces WHERE province_id = "{province[1:]}"' #4000
            )).fetchone()
            if query is None and not is_admin:
                await ctx.send(embed=interactions.Embed(description=f'Nie istnieje prowincja o ID **{province}**!'))
                connection.close()
                return
            province_id, province_name = query
        else:
            query = connection.execute(text(
                f'SELECT province_id, province_name FROM provinces WHERE province_name = "{province}"'  # [50, 'Jarawa']
            )).fetchone()
            if query is None and not is_admin:
                await ctx.send(embed=interactions.Embed(description=f'Nie istnieje prowincja o nazwie **{province}**!'))
                connection.close()
                return
            province_id, province_name = query

        number_of_buildings = connection.execute(text(
            f"""
                SELECT COUNT(*)
                FROM provinces NATURAL JOIN structures
                WHERE province_id = {province_id};
                """
        )).fetchone()[0]
        province_owner, province_controller, max_buildings = connection.execute(text(
            f"""
                SELECT country_id, controller_id, province_building_limit 
                FROM provinces NATURAL JOIN province_levels 
                WHERE province_id = {province_id}
            """
        )).fetchone()
        print(f'country_id = {country_id}')
        print(f'owner = {province_owner}')
        print(f'controller = {province_controller}')
        if (province_owner != country_id) and (not is_admin):
            await ctx.send(embed=interactions.Embed(description=f'Prowincja **{province_name} (#{province_id})**'
                                                                f' nie jest w pełni kontrolowana przez twoje państwo!'))
            connection.close()
            return

        costs = {}
        building = building.strip().split(',')  # ['2 Tartak', '2 Kopalnia']

        for b in building:
            print(b)

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
                connection.close()
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
                connection.close()
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
                      quantity = quantity + {int(b[0])}
                    """
                ))
            connection.commit()
            print(spawned_buildings)
            await ctx.send(embeds=interactions.Embed(
                title=f'Zespawnowano budynki w prowincji **{province_name} (#{province_id})!**',
                description=f'{spawned_buildings[2:]}'))
            connection.close()
            return

        if (number_of_buildings + sum(
                [int(i) for i in list(zip(*building))[0]])) > max_buildings:  # buildings + new_buildings > max
            await ctx.send(embed=interactions.Embed(
                description=f'W prowincji **{province_name} (#{province_id})**'
                            f' nie ma tyle miejsc na budynki!\n'
                            f'`{number_of_buildings} +'
                            f' {sum([int(i) for i in list(zip(*building))[0]])} > {max_buildings}`'))
            connection.close()
            return

        keys = ''
        for key in costs:  # {2: 1500, 4: 40, 5: 60}
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
                    print(f'jtem[1] = {jtem[1]}')
                    print(f'costs[jtem[0]] = {(costs[item[0]])}')
                    print(f'jtem[1] = {type(jtem[1])}')
                    print(f'costs[jtem[0]] = {type(costs[item[0]])}')
                    if jtem[1] > costs[jtem[0]]:
                        resources_required = resources_required + f', {jtem[2]} **{jtem[3]} [{jtem[1]}/{costs[jtem[0]]}]**'
                    else:
                        resources_required = resources_required + f', {jtem[2]} {jtem[3]} [{jtem[1]}/{costs[jtem[0]]}]'
                await ctx.send(
                    embed=interactions.Embed(description=f'Nie masz wystarczająco zasobów żeby wybudować budynki!\n'
                                                         f'{resources_required[2:]}'))
                connection.close()
                return

        for item in inventory:
            costs[item[0]] = [costs[item[0]], item[2], item[3]]  # {2: [1500, ':Talary:', 'Talary'], 4: [40,
            # ':Drewno:', 'Drewno'], 5: [60, ':Kamien:', 'Kamien']}

        # Everything checked, take resources and give buildings
        overall_cost = ''
        for key in costs:  # {2: [1500, ':Talary:', 'Talary'], 4: [40, ':Drewno:', 'Drewno']
            connection.execute(text(
                f"""
                UPDATE 
                  inventories
                SET 
                  quantity = quantity - {costs[key][0]} 
                WHERE country_id = {country_id} 
                AND item_id = {key};
                """
            ))
            overall_cost = overall_cost + f', **{costs[key][0]}** {costs[key][1]} {costs[key][2]}'
        built_buildings = ''
        for build in building:  # [['1', 'Tartak', ':tartak:, 1], ['2', 'Kopalnia', ':kopalnia:, 3]]
            connection.execute(text(
                f"""
                INSERT INTO structures (
                  province_id, building_id, quantity
                ) 
                VALUES 
                  ({province_id}, {build[3]}, {int(build[0])}) ON DUPLICATE KEY 
                UPDATE 
                  quantity = quantity + {int(build[0])}
                """
            ))
            built_buildings = built_buildings + f', **{build[0]}** {build[2]} {build[1]}'

        connection.commit()
        connection.close()
        await ctx.send(
            embeds=interactions.Embed(title=f'Wybudowano budynki w prowincji **{province_name} (#{province_id})!**',
                                      description=f'{built_buildings[2:]}\n'
                                                  f'Koszt: {overall_cost[2:]}'))
        connection.close()
        return
