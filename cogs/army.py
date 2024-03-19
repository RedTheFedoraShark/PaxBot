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

    @army.subcommand(description="Rekrutuje jednostki.")
    @interactions.option(name='prowincja', description='Nazwa/ID prowincji.')
    @interactions.option(name='jednostka', description='Nazwa/ID szablonu jednostki.')
    @interactions.option(name='nazwa_jednostki', description='Nazwa nowej jednostki.')
    @interactions.option(name='nazwa_armii', description='Nazwa nowej armii.')
    @interactions.option(name='admin', description='Jesteś admin?')
    async def recruit(self, ctx: interactions.CommandContext, prowincja: str, jednostka: str,
                      nazwa_jednostki: str = '', nazwa_armii: str = '', admin: str = ''):
        await ctx.defer()

        if admin != '' and await ctx.author.has_permissions(interactions.Permissions.ADMINISTRATOR):
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

        if prowincja.startswith('#'):
            prov = db.pax_engine.connect().execute(text(
                f'SELECT p.province_id, p.province_name '
                f'FROM provinces p '
                f'WHERE province_id = "{prowincja[1:]}" AND p.country_id = {country_id} '
                f'AND p.controller_id = {country_id}'
            )).fetchone()
            if not prov:
                await ctx.send(f"```ansi\n\u001b[0;31mNie kontrolujesz\u001b[0;0m w pełni prowincji o ID #{prowincja[1:]}.```")
                return
        else:
            prov = db.pax_engine.connect().execute(text(
                f'SELECT p.province_id, p.province_name '
                f'FROM provinces p '
                f'WHERE province_id = "{nprowincja}" AND p.country_id = {country_id} '
                f'AND p.controller_id = {country_id}'
            )).fetchone()
            if not prov:
                await ctx.send(
                    f"```ansi\n\u001b[0;31mNie kontrolujesz\u001b[0;0m w pełni prowincji o nazwie {prowincja}.```")
                return

        if jednostka.startswith('#'):
            unit = db.pax_engine.connect().execute(text(
                f'SELECT u.unit_template_id, u.unit_name '
                f'FROM units u '
                f'WHERE u.unit_template_id = "{jednostka[1:]}" AND u.country_id = {country_id}'
            )).fetchone()
            if not unit:
                await ctx.send(f"```ansi\nTwoje państwo \u001b[0;31mnie ma\u001b[0;0m szablonu jednostki o o ID #{jednostka[1:]}.```")
                return
        else:
            unit = db.pax_engine.connect().execute(text(
                f'SELECT u.unit_template_id, u.unit_name '
                f'FROM units u '
                f'WHERE u.unit_name = "{jednostka}" AND u.country_id = {country_id}'
            )).fetchone()
            if not unit:
                await ctx.send(
                    f"```ansi\nTwoje państwo \u001b[0;31mnie ma\u001b[0;0m szablonu jednostki o nazwie {jednostka}.```")
                return



        # Common Errors
        if len(nazwa_jednostki) > 20:
            await ctx.send(f"```ansi\nNazwa jednostki nie może mieć więcej niż \u001b[0;32m20\u001b[0;0m znaków!\n"
                           f"Nazwa '{nazwa_jednostki}' ma ich \u001b[0;31m{len(nazwa_jednostki)}\u001b[0;0m.```")
            return
        if len(nazwa_armii) > 20:
            await ctx.send(f"```ansi\nNazwa armii nie może mieć więcej niż \u001b[0;32m20\u001b[0;0m znaków!\n"
                           f"Nazwa '{nazwa_armii}' ma ich \u001b[0;31m{len(nazwa_armii)}\u001b[0;0m.```")
            return
        unit_names = db.pax_engine.connect().execute(text(
            f'SELECT unit_name FROM armies WHERE country_id = {country_id}'
        )).fetchall()
        unit_names = [item for sublist in unit_names for item in sublist]
        if nazwa_jednostki in unit_names:
            await ctx.send(f"```ansi\nMoże być tylko jedna jednostka z daną nazwą!\n```")
            return
        army_names = db.pax_engine.connect().execute(text(
            f'SELECT army_name FROM armies WHERE country_id = {country_id}'
        )).fetchall()
        army_names = [item for sublist in army_names for item in sublist]
        if nazwa_armii in army_names:
            await ctx.send(f"```ansi\nMoże być tylko jedna armia z daną nazwą!\n```")
            return

        # simply make an exception for admins and forget about it
        if admin != '' and await ctx.author.has_permissions(interactions.Permissions.ADMINISTRATOR):
            # teleport
            with db.pax_engine.connect() as conn:
                conn.begin()
                conn.execute(text(f'INSERT INTO armies (unit_template_id, country_id, province_id, army_id, army_visible) '
                                  f'VALUES '))
                conn.commit()
                conn.close()
            await ctx.send(f"```ansi\nPomyślnie zespawnowano jednostkę '{old[0][5]}' #{old[0][4]}.\n"
                           f"\u001b[1;31m'{old[0][1]}' #{old[0][2]}\u001b[0;0m ➤ \u001b[1;32m'{new[1]}' #{new[0]}\u001b[0;0m```")
            return

        # Player Errors

    @army.subcommand(description="Zmienia nazwę jednostki lub armii państwa.")
    @interactions.option(name='typ', description='Czemu chcesz zmienić nazwę?',
                         choices=[interactions.Choice(name="Armia", value="army"),
                                  interactions.Choice(name="Jednostka", value="unit")])
    @interactions.option(name='nazwa', description='Stara nazwa/ID wojska.')
    @interactions.option(name='nowa_nazwa', description='Nowa nazwa wojska.')
    async def rename(self, ctx: interactions.CommandContext, typ: str, nazwa: str, nowa_nazwa: str):
        await ctx.defer()
        country_id = db.pax_engine.connect().execute(text(
            f'SELECT country_id FROM countries NATURAL JOIN players WHERE player_id = "{ctx.author.id}"'
        )).fetchone()

        if await ctx.author.has_permissions(interactions.Permissions.ADMINISTRATOR):
            admin_bool = True
        else:
            admin_bool = False

        if typ == "army":
            keyword = "army"
            second = "armii"
        else:
            keyword = "unit"
            second = "jednostki"

        if nazwa.startswith('#'):
            old = db.pax_engine.connect().execute(text(
                f'SELECT {keyword}_id, {keyword}_name, country_id, country_name FROM armies NATURAL JOIN countries '
                f'WHERE {keyword}_id = "{nazwa[1:]}"'
            )).fetchone()
            if not old:
                await ctx.send(f"```ansi\nProwincja o ID #{nazwa[1:]} \u001b[0;31mnie istnieje\u001b[0;0m.```")
                return
        else:
            old = db.pax_engine.connect().execute(text(
                f'SELECT {keyword}_id, {keyword}_name, country_id, country_name FROM armies NATURAL JOIN countries '
                f'WHERE {keyword}_name = "{nazwa}"'
            )).fetchone()
            if not old:
                await ctx.send(f"```ansi\nProwincja o nazwie {nazwa} \u001b[0;31mnie istnieje\u001b[0;0m.```")
                return

        # Errors
        if len(nowa_nazwa) > 20:
            await ctx.send(f"```ansi\nNazwa {second} nie może mieć więcej niż \u001b[0;32m20\u001b[0;0m znaków!\n"
                           f"Nazwa '{nowa_nazwa}' ma ich \u001b[0;31m{len(nowa_nazwa)}\u001b[0;0m.```")
            return
        if '"' in nowa_nazwa:
            await ctx.send(f"```ansi\nNazwa {second} nie może mieć \u001b[0;31mcudzysłowu\u001b[0;0m!```")
            return
        if country_id[0] != old[2] and not admin_bool:
            await ctx.send(f"```ansi\nNie możesz zmienić nazwy {second} która do ciebie nie należy!```")
            return
        army_names = db.pax_engine.connect().execute(text(
            f'SELECT {keyword}_name FROM armies WHERE country_id = {country_id}'
        )).fetchall()
        army_names = [item for sublist in army_names for item in sublist]
        print(army_names)
        if nowa_nazwa in army_names:
            await ctx.send(f"```ansi\nMoże być tylko jedna jednostka/armia z daną nazwą!\n```")
            return

        with db.pax_engine.connect() as conn:
            conn.begin()
            conn.execute(text(f'UPDATE armies SET {keyword}_name = "{nowa_nazwa}" '
                              f'WHERE {keyword}_id = {old[0]}'))
            conn.commit()
            conn.close()
        # print(f'UPDATE provinces SET province_name = "{nowa_nazwa}" WHERE province_id = {province[0]}')
        await ctx.send(f"```ansi\nPomyślnie zmieniono nazwę {second} #{old[0]}.\n"
                       f"\u001b[1;31m'{old[1]}'\u001b[0;0m ➤ \u001b[1;32m'{nowa_nazwa}'\u001b[0;0m```")

    @army.subcommand(description="Dodaje rozkazy ruchu armii.")
    @interactions.option(name='armia', description='Nazwa/ID armii.')
    @interactions.option(name='granica', description='Do której prowincji chcesz ruszyć?')
    @interactions.option(name='admin', description='Jesteś admin?')
    async def move(self, ctx: interactions.CommandContext, armia: str, granica: str, admin: str = ''):
        await ctx.defer()

        # set up basic variables
        if admin != '' and await ctx.author.has_permissions(interactions.Permissions.ADMINISTRATOR):
            country_id = "%"
        else:
            country_id = db.pax_engine.connect().execute(text(
                f'SELECT country_id FROM countries NATURAL JOIN players WHERE player_id = "{ctx.author.id}"'
            )).fetchone()[0]

        if armia.startswith('#'):
            old = db.pax_engine.connect().execute(text(
                f'SELECT c.country_id, province_name, p.province_id, army_movement_left, a.army_id, a.army_name '
                f'FROM armies a NATURAL JOIN countries c '
                f'INNER JOIN provinces p ON a.province_id = p.province_id '
                f'WHERE army_id = "{armia[1:]}" AND c.country_id LIKE "{country_id}"'
            )).fetchall()
            if not old:
                await ctx.send(f"```ansi\n\u001b[0;31mNie posiadasz\u001b[0;0m armii o ID #{armia[1:]}.```")
                return
        else:
            old = db.pax_engine.connect().execute(text(
                f'SELECT c.country_id, province_name, p.province_id, army_movement_left, a.army_id, a.army_name  '
                f'FROM armies a NATURAL JOIN countries c '
                f'INNER JOIN provinces p ON a.province_id = p.province_id '
                f'WHERE army_name = "{armia}" AND c.country_id LIKE {country_id}'
            )).fetchall()
            if not old:
                await ctx.send(f"```ansi\n\u001b[0;31mNie posiadasz\u001b[0;0m armii o nazwie '{armia}'.```")
                return

        if granica.startswith('#'):
            new = db.pax_engine.connect().execute(text(
                f'SELECT province_id, province_name FROM provinces '
                f'WHERE province_id = "{granica[1:]}"'
            )).fetchone()
            if not new:
                await ctx.send(f"```ansi\nProwincja o ID #{granica[1:]} \u001b[0;31mnie istnieje\u001b[0;0m.```")
                return
        else:
            new = db.pax_engine.connect().execute(text(
                f'SELECT province_id, province_name FROM provinces '
                f'WHERE province_name = "{granica}"'
            )).fetchone()
            if not new:
                await ctx.send(f"```ansi\nProwincja o nazwie '{granica}' \u001b[0;31mnie istnieje\u001b[0;0m.```")
                return

        # simply make an exception for admins and forget about it
        if admin != '' and await ctx.author.has_permissions(interactions.Permissions.ADMINISTRATOR):
            # teleport
            with db.pax_engine.connect() as conn:
                conn.begin()
                conn.execute(text(f'UPDATE armies SET province_id = {new[0]} '
                                  f'WHERE army_id = {old[0][4]}'))
                conn.commit()
                conn.close()
            await ctx.send(f"```ansi\nPomyślnie przeteleportowano armię '{old[0][5]}' #{old[0][4]}.\n"
                           f"\u001b[1;31m'{old[0][1]}' #{old[0][2]}\u001b[0;0m ➤ \u001b[1;32m'{new[1]}' #{new[0]}\u001b[0;0m```")
            return

        # this is where the fun begins
        # the current location is old[4], but check for newest order
        current_province = db.pax_engine.connect().execute(text(
                f'SELECT target_province_id, province_name '
                f'FROM movement_orders m '
                f'INNER JOIN provinces p on m.target_province_id = p.province_id '
                f'WHERE m.army_id = {old[0][4]} '
                f'ORDER BY datetime DESC'
            )).fetchone()
        if not current_province:
            current_province = [old[0][2], old[0][3]]

        # get the border type
        print(current_province[0], new[0])
        border_type = db.pax_engine.connect().execute(text(
            f'SELECT border_type FROM borders '
            f'WHERE (province_id = {current_province[0]} AND province_id_2 = {new[0]}) '
            f'OR (province_id_2 = {current_province[0]} AND province_id = {new[0]})'
        )).fetchone()
        if not border_type:
            await ctx.send(f"```ansi\nNie ma granicy pomiędzy \u001b[0;31m'{current_province[1]}' #{current_province[0]}\u001b[0;0m "
                           f"i \u001b[0;32m'{new[1]}' #{new[0]}\u001b[0;0m.```")
            return
        if border_type[0] == 0:
            await ctx.send(f"```ansi\nNie możesz wejść na \u001b[0;31mWasteland\u001b[0;0m.```")
            return
        print(old)
        movements = set([moves[3] for moves in old])
        for move in movements:
            if border_type[0] > move:
                await ctx.send(f"```ansi\nArmia ma za mało ruchów."
                               f"\nPrzynajmniej jedna jednostka ma \u001b[0;31m{move}\u001b[0;0m, "
                               f"a potrzebne jest \u001b[0;32m{border_type[0]}\u001b[0;0m.```")
                return

        # remove movement and add order
        with db.pax_engine.connect() as conn:
            conn.begin()
            conn.execute(text(f'UPDATE armies SET army_movement_left = army_movement_left - {border_type[0]} '
                              f'WHERE army_id = {old[0][4]}'))
            conn.execute(text(f'INSERT INTO movement_orders (army_id, origin_province_id, target_province_id) '
                              f'VALUES ({old[0][4]}, {current_province[0]}, {new[0]})'))
            conn.commit()
            conn.close()

        await ctx.send(f"```ansi\nPomyślnie dodano rozkaz ruchu dla armii '{old[0][5]}' #{old[0][4]}.\n"
                       f"\u001b[1;31m'{current_province[1]}' #{current_province[0]}\u001b[0;0m ➤ \u001b[1;32m'{new[1]}' #{new[0]}\u001b[0;0m```")
        return

    @army.subcommand(description="Wyświetla rozkazy armii.")
    @interactions.option(name='typ', description='Które rozkazy chcesz wyświetlić?',
                         choices=[interactions.Choice(name="recruit", value="recruit"),
                                  interactions.Choice(name="reinforce", value="reinforce"),
                                  interactions.Choice(name="move", value="move")])
    @interactions.option(name='admin', description='Jesteś admin?')
    async def orders(self, ctx: interactions.CommandContext, typ: str, admin: str = ''):

        if admin != '' and await ctx.author.has_permissions(interactions.Permissions.ADMINISTRATOR):
            admin_bool = True
            if admin.startswith('<@') and admin.endswith('>'):  # if a ping
                country_id = db.pax_engine.connect().execute(text(
                    f'SELECT country_id FROM players NATURAL JOIN countries '
                    f'WHERE player_id = {admin[2:-1]}')).fetchone()
            else:
                country_id = db.pax_engine.connect().execute(text(
                    f'SELECT country_id FROM players NATURAL JOIN countries WHERE country_name = "{admin}"'
                )).fetchone()
        else:
            admin_bool = False
            country_id = db.pax_engine.connect().execute(text(
                f'SELECT country_id FROM countries NATURAL JOIN players WHERE player_id = "{ctx.author.id}"'
            )).fetchone()

        if typ == "army":
            return
        elif typ == "reinforce":
            return
        else:  # move

            if admin_bool and not country_id:
                country_id = ["%"]

            move_orders = db.pax_engine.connect().execute(text(
                f'SELECT mo.order_id, a.army_name, a.army_id, a.unit_name, a.unit_id, '
                f'p1.province_name, p1.province_id, p2.province_name, p2.province_id, mo.datetime '
                f'FROM movement_orders mo NATURAL JOIN armies a '
                f'INNER JOIN provinces p1 ON mo.origin_province_id = p1.province_id '
                f'INNER JOIN provinces p2 ON mo.target_province_id = p2.province_id '
                f'WHERE a.country_id = {country_id[0]} '
                f'ORDER BY datetime, order_id, army_id, unit_id ')).fetchall()

            if not move_orders:
                await ctx.send(f"```ansi\nTen kraj nie ma rozkazów ruchu dla armii.[0;0m.```")
                return

            embeds = await models.build_army_order_move(country_id)
            if len(embeds) == 1:
                await ctx.send(embeds=embeds[0])
                return
            pages = []
            for e in embeds:
                page = Page(embeds=e)
                pages.append(page)
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
