import interactions
from database import *
from sqlalchemy import text
import pandas as pd
import numpy as np
from config import models
from interactions.ext.paginators import Paginator
import json

with open("./config/config.json") as f:
    configure = json.load(f)


# all class names from this file have to be included in def below
def setup(bot):
    Province(bot)


class Province(interactions.Extension):
    # constructor
    def __init__(self, bot):
        self.bot = bot

    @interactions.slash_command(description='Testuj.', scopes=[configure['GUILD']])
    async def province(self, ctx):
        pass

    @province.subcommand(sub_cmd_description="Lista prowincji twojego państwa.")
    @interactions.slash_option(name='tryb', description='W jakim trybie wyświetlić informacje?',
                               opt_type=interactions.OptionType.STRING, required=True,
                               choices=[interactions.SlashCommandChoice(name="Dokładny", value="pages"),
                                        interactions.SlashCommandChoice(name="Prosty", value="list")])
    @interactions.slash_option(name='admin', description='Jesteś admin?',
                               opt_type=interactions.OptionType.STRING, )
    async def list(self, ctx: interactions.SlashContext, tryb: str, admin: str = ''):
        await ctx.defer()
        country_id = False
        index = 0
        if admin != "" and ctx.author.has_permission(interactions.Permissions.ADMINISTRATOR):
            admin_bool = True
            if admin.startswith('<@') and admin.endswith('>'):  # if a ping
                country_id = db.pax_engine.connect().execute(text(
                    f'SELECT country_id FROM players NATURAL JOIN countries '
                    f'WHERE player_id = {admin[2:-1]}')).fetchone()
            elif admin.startswith('#'):
                index = int(admin[1:]) - 1
            else:
                country_id = db.pax_engine.connect().execute(text(
                    f'SELECT country_id FROM players NATURAL JOIN countries WHERE country_name = "{admin}"'
                )).fetchone()
        else:
            admin_bool = False

        number_of_provinces = db.pax_engine.connect().execute(text(
            f'SELECT COUNT(*) FROM provinces'
        )).fetchone()[0]

        if tryb == "pages":
            if admin_bool:
                # print(f"CountryId {country_id}")
                if country_id:
                    province_ids = db.pax_engine.connect().execute(text(
                        f'SELECT province_id FROM provinces NATURAL JOIN countries '
                        f'WHERE country_id = {country_id[0]} OR controller_id = {country_id[0]}')).fetchall()
                else:
                    province_ids = list((x,) for x in range(1, number_of_provinces + 1))
            else:
                country_id = db.pax_engine.connect().execute(text(
                    f'SELECT country_id FROM players NATURAL JOIN countries WHERE player_id = "{ctx.author.id}"'
                )).fetchone()
                province_ids = db.pax_engine.connect().execute(text(
                    f'SELECT province_id FROM provinces NATURAL JOIN countries '
                    f'WHERE country_id = {country_id[0]} OR controller_id = {country_id[0]}')).fetchall()
            non_dup_ids = set()
            for province_id in province_ids:
                non_dup_ids.add(province_id[0])
            non_dup_ids = sorted(non_dup_ids)

            province_incomes = {}
            summed_province_incomes = {}

            province_incomes = models.get_provinces_income()
            for province_id in non_dup_ids:
                summed_province_incomes[province_id] = models.sum_item_incomes({province_id: province_incomes[province_id]})
            print(summed_province_incomes[50])
            print(type(summed_province_incomes[50].controller_id))
            all_province_incomes = models.get_hunger(summed_province_incomes)
            all_province_incomes['province_incomes'] = province_incomes

            pages = []
            if not country_id:
                country_id = [0]
            for province_id in non_dup_ids:
                page = await models.build_province_embed(self, province_id, country_id[0], all_province_incomes)
                # if returned value is a list, unpack it
                if isinstance(page, list):
                    for p in page:
                        pages.append(p)
                else:
                    pages.append(page)

            paginator = Paginator.create_from_embeds(ctx.client, *pages)
            paginator.page_index = index
            await paginator.send(ctx=ctx)
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
            # print(df.to_markdown(index=False))
            # print(len(df.to_markdown(index=False)))
            if len(df.to_markdown(index=False)) < 1990:
                await ctx.send(f"```ansi\n{df.to_markdown(index=False)}```")
            else:
                df = df.to_markdown(index=False).split("\n")
                pages = await models.pagify(df, max_char=1860)

                paginator = Paginator.create_from_string(ctx.client, df, page_size=4000)
                # paginator.page_index = index
                await paginator.send(ctx=ctx)

    @province.subcommand(sub_cmd_description="Zmiana nazwy twojej prowincji.")
    @interactions.slash_option(name='nazwa', description='#ID albo obecna nazwa prowincji.',
                               opt_type=interactions.OptionType.STRING, required=True)
    @interactions.slash_option(name='nowa_nazwa', description='Nowa nazwa prowincji do 17 znaków.',
                               opt_type=interactions.OptionType.STRING, required=True)
    async def rename(self, ctx: interactions.SlashContext, nazwa: str, nowa_nazwa: str):
        await ctx.defer()
        nazwa.strip()
        nowa_nazwa.strip()

        country_id = db.pax_engine.connect().execute(text(
            f'SELECT country_id FROM countries NATURAL JOIN players WHERE player_id = "{ctx.author.id}"'
        )).fetchone()

        if ctx.author.has_permission(interactions.Permissions.ADMINISTRATOR):
            admin_bool = True
        else:
            admin_bool = False

        if nazwa.startswith('#'):
            province = db.pax_engine.connect().execute(text(
                f'SELECT province_id, province_name, country_id, country_name FROM provinces NATURAL JOIN countries '
                f'WHERE province_id = "{nazwa[1:]}"'
            )).fetchone()
        else:
            province = db.pax_engine.connect().execute(text(
                f'SELECT province_id, province_name, country_id, country_name FROM provinces NATURAL JOIN countries '
                f'WHERE province_name = "{nazwa}"'
            )).fetchone()

        # Errors
        if len(nowa_nazwa) > 17:
            await ctx.send(f"```ansi\nNazwa prowincji nie może mieć więcej niż \u001b[0;32m17\u001b[0;0m znaków!\n"
                           f"Nazwa '{nowa_nazwa}' ma ich \u001b[0;31m{len(nowa_nazwa)}\u001b[0;0m.```")
            return
        if '"' in nowa_nazwa:
            await ctx.send(f"```ansi\nNazwa prowincji nie może mieć \u001b[0;31mcudzysłowu\u001b[0;0m!```")
            return
        if country_id[0] != province[2] and not admin_bool:
            await ctx.send(f"```ansi\nNie możesz zmienić nazwy prowincji która do ciebie nie należy!\n"
                           f"Prowincja '{province[1]}' \u001b[0;30m({province[0]}) \u001b[0;0m "
                           f"należy do państwa '{province[3]}'.```")
            return
        all_names = db.pax_engine.connect().execute(text(
            f'SELECT province_name FROM provinces'
        )).fetchall()
        all_names = [item for sublist in all_names for item in sublist]
        # print(all_names)
        if nowa_nazwa in all_names:
            await ctx.send(f"```ansi\nMoże być tylko jedna prowincja z daną nazwą!\n```")
            return

        with db.pax_engine.connect() as conn:
            conn.begin()
            conn.execute(text(f'UPDATE provinces SET province_name = "{nowa_nazwa}"'
                              f'WHERE province_id = {province[0]}'))
            conn.commit()
            conn.close()
        # print(f'UPDATE provinces SET province_name = "{nowa_nazwa}" WHERE province_id = {province[0]}')
        await ctx.send(f"```ansi\nPomyślnie zmieniono nazwę prowincji #{province[0]}.\n"
                       f"\u001b[1;31m'{province[1]}'\u001b[0;0m ➤ \u001b[1;32m'{nowa_nazwa}'\u001b[0;0m```")

