import interactions
from sqlalchemy import text
from database import *
from config import models
from interactions.ext.paginator import Page, Paginator


# all class names from this file have to be included in def below
def setup(bot):
    Army(bot)


class Army(interactions.Extension):
    # constructor
    def __init__(self, bot):
        self.bot = bot

    @interactions.extension_command(description='Ściąga z komendami Pax Zeonica.', scope='917078941213261914')
    async def army(self, ctx):
        pass

    @army.subcommand(description="Lista armii twojego państwa.")
    @interactions.option(name='tryb', description='W jakim trybie wyświetlić informacje?',
                         choices=[interactions.Choice(name="Dokładny", value="pages"),
                                  interactions.Choice(name="Prosty", value="list")])
    @interactions.option(name='admin', description='Jesteś admin?')
    async def list(self, ctx: interactions.CommandContext, tryb: str, admin: str = ''):
        await ctx.defer()
        country_id = False
        if admin != "" and await ctx.author.has_permissions(interactions.Permissions.ADMINISTRATOR):
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
        if tryb == "pages":
            if admin_bool:
                print(f"CountryId {country_id}")
                if country_id:
                    unit_ids = db.pax_engine.connect().execute(text(
                        f'SELECT unit_id FROM armies NATURAL JOIN countries '
                        f'WHERE country_id = {country_id[0]}')).fetchall()
                else:
                    # '%' is a wildcard for SQL select: SELECT unit_id FROM armies WHERE country_id = '%';
                    unit_ids = '%'
            else:
                country_id = db.pax_engine.connect().execute(text(
                    f'SELECT country_id FROM players NATURAL JOIN countries WHERE player_id = "{ctx.author.id}"'
                )).fetchone()
                unit_ids = db.pax_engine.connect().execute(text(
                    f'SELECT unit_id FROM armies NATURAL JOIN countries '
                    f'WHERE country_id = {country_id[0]}')).fetchall()
            non_dup_ids = set()
            for x in unit_ids:
                non_dup_ids.add(x[0])
            non_dup_ids = sorted(non_dup_ids)
            pages = []
            if not country_id:
                country_id = [0]
            for x in non_dup_ids:
                #######################################################################################################
                page = await models.build_province_embed(x, country_id[0])
                # if returned value is a list, unpack it
                if isinstance(page, list):
                    for p in page:
                        pages.append(Page(embeds=p))
                else:
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
            ###########################################################################################################
        else:
            if admin_bool:
                if country_id:
                    df = await models.build_army_list(country_id[0])  # To trzeba zrobić
                else:
                    df = await models.build_army_list_admin()  # To trzeba zrobić
            else:
                country_id = db.pax_engine.connect().execute(text(
                    f'SELECT country_id FROM players NATURAL JOIN countries '
                    f'WHERE player_id = {ctx.author.id}')).fetchone()
                df = await models.build_army_list(country_id[0])
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
    @interactions.extension_command(
        description="manage armies"
    )
    async def army(self, ctx: interactions.CommandContext):
        return

    @army.subcommand(
        description="List armies"
    )
    async def list(self, ctx: interactions.CommandContext, target: str=None, admin: bool = False):
        connection = db.pax_engine.connect()
        original_input = target
        MODE = 'country'
        if target is None:
            target = connection.execute(
                text(f'SELECT country_id FROM players WHERE player_id = {ctx.author.id};')).fetchone()[0]
        else:
            target = target.strip()

            if target.startswith('<@') and target.endswith('>'):
                target = connection.execute(
                    text(f'SELECT country_id FROM players WHERE player_id = {target[2:-1]};')).fetchone()[0]
            elif target.startswith('#'):
                MODE = 'province'
                # select from borders twice, zip and check if the proince is seen by the player
                # visible
            else:
                pass

        if target == None:
            await ctx.send(f'There is no such {MODE} as "{original_input}".')
            return


        connection.close()
        return
"""
