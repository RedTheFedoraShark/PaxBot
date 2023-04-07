import interactions
from database import *
from sqlalchemy import text
import pandas as pd
import numpy as np
from config import models
from interactions.ext.paginator import Page, Paginator


def province_income(income: list, province_id: int):
    connection = db.pax_engine.connect()
    # 1.1 Grabbing modifiers for the province (pops, autonomy and terrains)
    query = connection.execute(
        text(f"SELECT SUM(building_workers * quantity), province_pops, province_autonomy, terrain_id, "
             f"country_id "
             f"FROM provinces NATURAL JOIN structures NATURAL JOIN buildings "
             f"WHERE province_id = {province_id}")).fetchone()
    if query[0] is None and query[4] in (253, 254, 255):
        return income
    elif query[0] is None:
        # 1.2 I love the IRS :)
        autonomy_modifier = (100 - query[2]) / 100
        income.append((query[4], 2, (int(query[1]) * 0.25) * autonomy_modifier))
        return income
    print(query)
    population_modifier = query[1] / int(query[0])
    if population_modifier > 1:
        population_modifier = 1
    autonomy_modifier = (100 - query[2]) / 100
    print(population_modifier, autonomy_modifier)
    # 1.2 I love the IRS :)
    income.append((query[4], 2, (int(query[1]) * 0.25) * autonomy_modifier))
    # 1.3 Bierzemy budynki jakie są w prowincji (typ budynku, ilość) i zbieramy info o ich przychodzie
    # (typ itemu, ilość) oraz modyfikator terenu
    query2 = connection.execute(
        text(f"SELECT building_id, quantity, item_id, item_quantity, modifier "
             f"FROM provinces NATURAL JOIN structures NATURAL JOIN buildings NATURAL JOIN buildings_production "
             f"NATURAL JOIN terrains_modifiers "
             f"WHERE terrain_id={query[3]}")).fetchall()
    print(query2)
    # Liczymy produkcję dla danego typu budynku, w danej prowincji
    # production_quantity = ilość_budynków * (produkcja_budynku * (mod_populacji * mod_autonomii * mod_terenu))
    # production_quantity = 3 * (10 * (0.785 * 0.5 * 1.5))
    for row in query2:
        terrain_modifier = (100 + row[4]) / 100
        print(terrain_modifier)
        if row[3] < 0:
            production_quan = row[3]
        else:
            production_quan = row[1] * (row[3] * (population_modifier * autonomy_modifier * terrain_modifier))
        income.append((query[4], row[2], production_quan))
    return income


def setup(bot):
    Province(bot)


class Province(interactions.Extension):
    # constructor
    def __init__(self, bot):
        self.bot = bot

    @interactions.extension_command(description='Testuj.', scope='917078941213261914')
    async def province(self, ctx):
        pass

    @province.subcommand(description="Lista prowincji twojego państwa.")
    @interactions.option(name='tryb', description='W jakim trybie wyświetlić informacje?',
                         choices=[interactions.Choice(name="Dokładny", value="pages"),
                                  interactions.Choice(name="Prosty", value="list")])
    @interactions.option(name='admin', description='Jesteś admin?')
    async def list(self, ctx: interactions.CommandContext, tryb: str, admin: str = ''):
        # God forgive me for what I have done with this code.
        country_id = False
        index = 0
        if admin != "" and await ctx.author.has_permissions(interactions.Permissions.ADMINISTRATOR):
            admin_bool = True
            if admin.startswith('<@') and admin.endswith('>'):  # if a ping
                country_id = db.pax_engine.connect().execute(text(
                    f'SELECT country_id FROM players NATURAL JOIN countries '
                    f'WHERE player_id = {admin[2:-1]}')).fetchone()
            elif admin.startswith('#'):
                index = int(admin[1:]) - 1
        else:
            admin_bool = False

        if tryb == "pages":
            if admin_bool:
                if country_id:
                    province_ids = db.pax_engine.connect().execute(text(
                        f'SELECT province_id FROM players NATURAL JOIN countries NATURAL JOIN provinces '
                        f'WHERE country_id = {country_id[0]}')).fetchall()
                else:
                    province_ids = list((x, ) for x in range(1, 322))
            else:
                province_ids = db.pax_engine.connect().execute(text(
                    f'SELECT province_id FROM players NATURAL JOIN countries NATURAL JOIN provinces '
                    f'WHERE player_id = {ctx.author.id}')).fetchall()
            non_dup_ids = set()
            for x in province_ids:
                non_dup_ids.add(x[0])
            non_dup_ids = sorted(non_dup_ids)
            pages = []
            for x in non_dup_ids:
                page = await models.build_province_embed(x)
                pages.append(Page(embeds=page))
            if len(pages) > 25:
                use = True
            else:
                use = False
            await Paginator(
                client=self.bot,
                ctx=ctx,
                author_only=True,
                timeout=600,
                use_index=use,
                index=index,
                message="test",
                pages=pages
            ).run()
        else:
            if admin_bool:
                if country_id:
                    df = await models.build_province_list(country_id[0])
                else:
                    df = await models.build_province_list_admin()
            else:
                country_id = db.pax_engine.connect().execute(text(
                    f'SELECT country_id FROM players NATURAL JOIN countries '
                    f'WHERE player_id = {ctx.author.id}')).fetchone()
                df = await models.build_province_list(country_id[0])
            if len(df.to_markdown(index=False)) < 1990:
                await ctx.send(f"```ansi\n{df.to_markdown(index=False)}```")
            else:
                df = df.to_markdown(index=False).split("\n")
                pages = await models.pagify(df)

                await Paginator(
                    client=self.bot,
                    ctx=ctx,
                    author_only=True,
                    timeout=600,
                    message="test",
                    pages=pages
                ).run()

    """
    @interactions.extension_command(description='dummy')
    async def province(self, ctx: interactions.CommandContext):
        return

    @province.subcommand(description='')
    @interactions.option(name='country', description='Podaj nazwę państwa lub oznacz gracza')
    async def list(self, ctx: interactions.CommandContext(), country: str):

        await ctx.defer()
        connection = db.pax_engine.connect()
        if country.startswith('<@') and country.endswith('>'): # if a ping
            result = connection.execute(
                text(f'SELECT country_name, country_id FROM players NATURAL JOIN countries WHERE player_id = {country[2:-1]}')).fetchone()
            if result is None:
                await ctx.send('Ten gracz nie ma przypisanego państwa.')
                connection.close()
                return
            country = result[1]
        elif country != '':
            result = connection.execute(
                text(f'SELECT country_name, country_id FROM countries WHERE country_name = "{country}"')).fetchone()
            if result is None:
                await ctx.send('Takie państwo nie istnieje.')
                connection.close()
                return
            country = result[1]
        else:
            country = connection.execute(
                text(f'SELECT country_name, country_id from players NATURAL JOIN countries WHERE player_id = {ctx.author.id};')).fetchone()[1]

        result = connection.execute(
            text(f'SELECT province_id, province_name, region_name, terrain_name, good_name, '
                 f'religion_name, country_name, province_pops, province_pops_used, province_autonomy '
                 f'FROM provinces '
                 f'NATURAL JOIN terrains '
                 f'NATURAL JOIN goods '
                 f'NATURAL JOIN regions '
                 f'NATURAL JOIN religions'
                 f'NATURAL JOIN countries'
                 f'WHERE country_id = 1'))

        connection.close()
        return

    @province.subcommand(description='a')
    @interactions.option(name='proivnce', description='Nazwa lub id prowincji.')
    async def details(self, ctx: interactions.CommandContext, province: str):

        self.bot.defer()
        connection = db.pax_engine.connect()



        result = connection.execute(
            text(f'SELECT province_id, province_name, region_name, terrain_name, good_name, '
                 f'religion_name, country_name, province_pops, province_pops_used, province_autonomy '
                 f'FROM provinces '
                 f'NATURAL JOIN terrains '
                 f'NATURAL JOIN goods '
                 f'NATURAL JOIN regions '
                 f'NATURAL JOIN religions'
                 f'NATURAL JOIN countries'
                 f'WHERE country_id = 1'))


        connection.close()
        return

    @province.subcommand(description='a')
    async def give(self, ctx: interactions.CommandContext):
        pass
    """
