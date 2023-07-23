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
    async def list(self, ctx: interactions.CommandContext, province: str='', country: str='', admin:bool=False):
        if admin and ctx.author.has_permissions(interactions.Permissions.ADMINISTRATOR):
            is_admin = True
        else:
            is_admin = False

        connection = db.pax_engine.connect()

        province, country = province.strip(), country.strip()

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
                text(f'SELECT country_id from players NATURAL JOIN countries WHERE player_id = {ctx.author.id};')).fetchone()[0]
            if country is None:
                if not is_admin:
                    await ctx.send('Nie masz przypisanego państwa!')
                else:
                    await ctx.send('Państwo nie może być puste!')
                return

        if province[0] == '#':
            result = connection.execute(
                text(f'SELECT province_id FROM provinces WHERE province_id = {province[1:]};')).fetchone()
            if result is None:
                await ctx.send('Dupa')
                return
            province = result[0]
        elif province != '':
            province = connection.execute(
                text(f'SELECT province_id FROM provinces WHERE province_name = "{province}";')).fetchone()[0]
            if province is None:
                await ctx.send('Pojebało cię dziewczynko')
                return

        if is_admin:
            if province != '':
                result = connection.execute(
                    text(f'SELECT province_id, province_name, building_name'))

            elif country != '':
        else:
            pass




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

    @building.subcommand(description='')
    async def destroy(self):
        return

    @building.subcommand(description='')
    async def upgrade(self):
        return
