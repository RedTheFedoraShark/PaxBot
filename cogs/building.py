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
    @interactions.slash_option(name='province', description='#Id lub nazwa prowincji',
                               opt_type=interactions.OptionType.STRING)
    @interactions.slash_option(name='country', description='Nazwa państwa lub ping',
                               opt_type=interactions.OptionType.STRING)
    @interactions.slash_option(name='admin', description='Admin?',
                               opt_type=interactions.OptionType.BOOLEAN)
    async def list(self, ctx: interactions.SlashContext, province: str = '', country: str = '', admin: bool = False):
        if admin and ctx.author.has_permission(interactions.Permissions.ADMINISTRATOR):
            is_admin = True
        else:
            is_admin = False

        connection = db.pax_engine.connect()

        province, country = province.strip(), country.strip()

        if country.startswith('<@') and country.endswith('>'):  # if a ping
            # id = panstwo[2:-1]
            result = connection.execute(
                text(
                    f'SELECT country_id FROM players NATURAL JOIN countries WHERE player_id = {country[2:-1]}')).fetchone()
            if result is None:
                await ctx.send('Ten gracz nie ma przypisanego państwa.')
                connection.close()
                return
            country = result[0]
        elif country != '':
            result = connection.execute(
                text(f'SELECT country_id FROM countries WHERE country_name = "{country}"')).fetchone()
            if result is None:
                await ctx.send('Takie państwo nie istnieje.')
                connection.close()
                return
        else:
            country = connection.execute(
                text(
                    f'SELECT country_id from players NATURAL JOIN countries WHERE player_id = {ctx.author.id};')).fetchone()[
                0]
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
                await ctx.send('Dupa')
        else:
            pass

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
            if admin.startswith('<@') and admin.endswith('>'):  # if a ping
                country_id = db.pax_engine.connect().execute(text(
                    f'SELECT country_id FROM players NATURAL JOIN countries '
                    f'WHERE player_id = {admin[2:-1]}')).fetchone()[0]
            else:
                country_id = db.pax_engine.connect().execute(text(
                    f'SELECT country_id FROM players NATURAL JOIN countries WHERE country_name = "{admin}"'
                )).fetchone()[0]
        else:
            country_id = db.pax_engine.connect().execute(text(
                f'SELECT country_id FROM countries NATURAL JOIN players WHERE player_id = "{ctx.author.id}"'
            )).fetchone()[0]

        pages = [await models.bt_list(self, country_id=country_id)]
        connection.close()

        if len(pages) == 1:
            await ctx.send(embed=pages[0])
        else:
            paginator = Paginator.create_from_embeds(ctx.client, *pages)
            await paginator.send(ctx=ctx)

        return

    @building.subcommand(sub_cmd_description='Budowanie budynków')
    @interactions.slash_option(name='building', description='Jaki budynek chcesz zbudować',
                               opt_type=interactions.OptionType.STRING, required=True)
    @interactions.slash_option(name='province', description='W jakiej prowincji chcesz zbudować budynek?',
                               opt_type=interactions.OptionType.STRING, required=True)
    @interactions.slash_option(name='admin', description='Admin?',
                               opt_type=interactions.OptionType.BOOLEAN)
    async def build(self, ctx: interactions.SlashContext, building: str, province: str, admin: bool):
        connection = db.pax_engine.connect()
        country = None
        is_admin = ctx.author.has_permission(interactions.Permissions.ADMINISTRATOR)
        if admin and not is_admin:
            await ctx.send('Nie masz uprawnień administratora.')
            return
        elif not admin:
            result = connection.execute(
                text(f'SELECT country_id FROM players WHERE player_id = {ctx.author.id};')).fetchone()
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
            text(
                f'SELECT province_id FROM structures WHERE province_id = {province} AND building_id = {building};')).fetchone()
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


"""
    @building.subcommand(description='')
    async def destroy(self):
        return

    @building.subcommand(description='')
    async def upgrade(self):
        return
"""
