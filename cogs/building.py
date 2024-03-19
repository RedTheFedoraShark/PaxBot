import interactions
from database import *
from sqlalchemy import text
from config import models
from interactions.ext.paginator import Page, Paginator


# all class names from this file have to be included in def below
def setup(bot):
    Template(bot)


class Template(interactions.Extension):
    # constructor
    def __init__(self, bot):
        self.bot = bot

    @interactions.extension_command(description='Zarządzanie budynkami')
    async def building(self, ctx: interactions.CommandContext):
        pass

    @building.subcommand(description='Lista twoich zbudowanych budynków')
    @interactions.option(description='#Id lub nazwa prowincji')
    @interactions.option(description='Nazwa państwa lub ping')
    @interactions.option(description='Admin?')
    async def list(self, ctx: interactions.CommandContext, province: str = '.', country: str = '', admin: bool = False):
        if admin and ctx.author.has_permissions(interactions.Permissions.ADMINISTRATOR):
            is_admin = True
        else:
            is_admin = False

        connection = db.pax_engine.connect()

        province, country = province.strip(), country.strip()

        ##
        ## Check country variable
        ##
        if country.startswith('<@') and country.endswith('>'): # if a ping
            # id = panstwo[2:-1]
            result = connection.execute(
                text(f'SELECT country_id FROM players NATURAL JOIN countries WHERE player_id = {country[2:-1]}')).fetchone()
            if result is None:
                await ctx.send('Ten gracz nie ma przypisanego państwa.')
                connection.close()
                return
            country = result[0]
        elif country != '':
            result = connection.execute(text(f'SELECT country_id FROM countries WHERE country_name = "{country}"')).fetchone()
            if result is None:
                await ctx.send('Takie państwo nie istnieje.')
                connection.close()
                return
        else:
            country = connection.execute(
                text(f'SELECT country_id from players NATURAL JOIN countries WHERE player_id = {ctx.author.id};')).fetchone()
            if country is None:
                if not is_admin:
                    await ctx.send('Nie masz przypisanego państwa!')
                elif province == '':
                    await ctx.send('Państwo nie może być puste gdy nie ma podanej prowincji!')
                return
            country = country[0]

        ### origin country check
        origin_country = connection.execute(
            text(
                f'SELECT country_id from players NATURAL JOIN countries WHERE player_id = {ctx.author.id};')).fetchone()
        if origin_country is None and not is_admin:
            await ctx.send('Nie masz przypisanego państwa!')
            return
        origin_country = origin_country[0]

        ###
        ### Check province variable
        ###
        if province[0] == '#':
            result = connection.execute(
                text(f'SELECT province_id FROM provinces WHERE province_id = {province[1:]};')).fetchone()
            if result is None:
                await ctx.send('Nieprawidłowe id prowincji!')
                return
            province = result[0]
        elif province != '':
            province = connection.execute(
                text(f'SELECT province_id FROM provinces WHERE province_name = "{province}";')).fetchone()
            if province is None:
                await ctx.send('Pojebało cię dziewczynko')
                return
            province = province[0]

        ###
        ### Get specific info based on variables
        ### First check for province
        ### Then check for country
        ###
        if is_admin:
            if province != '':
                result = connection.execute(
                    text(f'SELECT building_name '
                         f'FROM provinces NATURAL JOIN structures '
                         f'WHERE province_id = {province} '
                         f'ORDER BY building_name ASC;')).fetchall()
                embed = models.bl_province(result)

            elif country != '':
                result = connection.execute(
                    text(f'SELECT province_id, province_name, building_name '
                         f'FROM provinces NATURAL JOIN structures '
                         f'WHERE country_id = {country}'
                         f'ORDER BY province_id, building name ASC;')).fetchall()
                embed = models.bl_country(result)
        else:
            # visibility check
            visible = connection.execute(
                text(f'SELECT province_id FROM armies WHERE country_id = {origin_country} '
                     f'UNION '
                     f'SELECT province_id FROM provinces WHERE controller_id = {origin_country};')).fetchall()
            list = '('
            for prov in visible:
                list += f'{prov[0]},'
            list = list[:-1] + ')'

            all_visible = connection.execute(
                text(f'SELECT province_id FROM borders WHERE province_id in {list} '
                     f'UNION '
                     f'SELECT province_id_2 FROM borders WHERE province_id_2 in {list};')).fetchall()
            list = '('
            for prov in visible:
                list += f'{prov[0]},'
            list = list[:-1] + ')'

            if province != '':
                visible = False
                for p in all_visible:
                    if province in p:
                        visible = True
                if visible:
                    result = connection.execute(
                        text(f'SELECT province_id, province_name, structures.building_id, building_name '
                             f'FROM provinces NATURAL JOIN structures INNER JOIN buildings on structures.building_id = buildings.building_id '
                             f'WHERE provinces.province_id = {province}'
                             f';')).fetchall()
                    embed = models.bl_province(result)
                else:
                    await ctx.send('Ta prowincja jest spowita mgłą wojny!')
                    return

            elif country != '':
                result = connection.execute(
                    text(f'SELECT province_id, province_name, structures.building_id, building_name '
                         f'FROM provinces NATURAL JOIN structures NATURAL JOIN buildings '
                         f'WHERE country_id = {country} and province_id in {list} '
                         f'ORDER BY province_id, building name ASC;')).fetchall()
                embed = models.bl_country(result)
        await ctx.send(embeds=embed)
        return

    @building.subcommand(description='Lista twoich szablonów budynków')
    async def templates(self, ctx: interactions.CommandContext):
        await ctx.defer()
        connection = db.pax_engine.connect()

        country = connection.execute(text(f'SELECT country_id FROM players WHERE player_id = {ctx.author.id};')).fetchone()
        if country is None:
            country = 255
        else:
            country = country[0]

        buildings = connection.execute(
            text(f'SELECT building_id, building_name, building_desc, building_emoji, building_image_url '
                 f'FROM country_buildings NATURAL JOIN buildings '
                 f'WHERE country_id in ({country}, 255) ORDER BY building_id DESC;')).fetchall()
        pages = [Page(embeds=models.bt_list(buildings))] + [Page(embeds=models.bt_detail(building, connection)) for building in buildings]
        connection.close()
        await Paginator(
            client=self.bot,
            ctx=ctx,
            author_only=True,
            timeout=300,
            message="dupa",
            use_index=True,
            index=0,
            pages=pages
        ).run()
        return

    @building.subcommand(description='Budowanie budynków')
    @interactions.option(description='Jaki budynek chcesz zbudować')
    @interactions.option(description='W jakiej prowincji chcesz zbudować budynek?')
    @interactions.option(description='Czy jesteś adminem?')
    async def build(self, ctx: interactions.CommandContext, building: str, province: str, admin: bool):
        connection = db.pax_engine.connect()
        country = None
        is_admin = await ctx.author.has_permissions(interactions.Permissions.ADMINISTRATOR)
        if admin and not is_admin:
            await ctx.send('Nie masz uprawnień administratora.')
            return
        elif not admin:
            result = connection.execute(text(f'SELECT country_id FROM players WHERE player_id = {ctx.author.id};')).fetchone()
            if result is not None:
                country = result[0]
            else:
                await ctx.send('Nie masz przypisanego państwa.')
                return

        building, province = building.strip(), province.strip()
        result = connection.execute(
            text(f'SELECT building_id, building_name FROM buildings NATURAL JOIN country_buildings '
                 f'WHERE building_name = "{building}" AND country_id in ({country},255);')).fetchone()

        if result is None:
            await ctx.send('Taki budynek nie istnieje!')
            return
        building = result[0]
        b_name = result[1]

        if province[0] == '#':
            result = connection.execute(
                text(f'SELECT province_id, province_name FROM provinces '
                     f'WHERE country_id = {country} AND province_id = {province[1:]}')).fetchone()
        else:
            result = connection.execute(
                text(f'SELECT province_id, province_name FROM provinces '
                     f'WHERE country_id = {country} AND province_name = {province};')).fetchone()

        if result is None:
            await ctx.send('Taka prowincja nie istnieje lub nie jesteś jej właścicielem!')
            return
        province = result[0]
        p_name = result[1]
        result = connection.execute(
            text(f'SELECT province_id FROM structures WHERE province_id = {province} AND building_id = {building};')).fetchone()
        if result is not None:
            await ctx.send(f'{b_name} już istenieje w prowincji {p_name}(#{province})!')
            return

        connection.rollback()
        connection.begin()

        try:
            connection.execute(text(f'INSERT INTO structures VALUES ({building}, {province})'))
        except:
            await ctx.send('Something went terribly wrong!')
            connection.rollback()
            connection.close()
            return

        connection.commit()
        connection.close()
        return

    @building.subcommand(description='a')
    async def destroy(self):
        return

    @building.subcommand(description='b')
    async def upgrade(self):
        return
