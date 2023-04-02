import interactions
from interactions.ext.paginator import Page, Paginator
from database import *
from config import models
from sqlalchemy import text
import time
import json

with open("./config/config.json") as f:
    config = json.load(f)


def setup(bot):
    Info(bot)


class Info(interactions.Extension):

    def __init__(self, bot):
        self.bot = bot

    @interactions.extension_command(description='Ściąga z komendami Pax Zeonica.', scope='917078941213261914')
    async def commands(self, ctx):
        await ctx.send(embeds=models.commands())

    @interactions.extension_command(description='Testuj', scope='917078941213261914')  # , scope='917078941213261914'
    async def info(self, ctx: interactions.CommandContext):
        pass

    @info.subcommand(description="Informacje o komendach.")
    @interactions.option(name="nazwa_komendy", description='Wpisz nazwę komendy którą chcesz sprawdzić.', required=True,
                         choices=[  # Information
                                  interactions.Choice(name="/tutorial", value=0),
                                  interactions.Choice(name="/commands", value=1),
                                  interactions.Choice(name="/info command", value=2),
                                  interactions.Choice(name="/info country", value=3),
                                  interactions.Choice(name="/map", value=4),
                                    # Inventory
                                  interactions.Choice(name="/inventory list", value=5),
                                  interactions.Choice(name="/inventory item", value=6),
                                  interactions.Choice(name="/inventory give", value=7),
                                    # Army
                                  interactions.Choice(name="/army list", value=8),
                                  interactions.Choice(name="/army templates", value=9),
                                  interactions.Choice(name="/army recruit", value=10),
                                  interactions.Choice(name="/army disband", value=11),
                                  interactions.Choice(name="/army reorg", value=12),
                                  interactions.Choice(name="/army rename", value=13),
                                    # Buildings
                                  interactions.Choice(name="/building list", value=14),
                                  interactions.Choice(name="/building templates", value=15),
                                  interactions.Choice(name="/building build", value=16),
                                  interactions.Choice(name="/building destroy", value=17),
                                  interactions.Choice(name="/building upgrade", value=18),
                                    # Provinces
                                  interactions.Choice(name="/province list", value=19),
                                  interactions.Choice(name="/province rename", value=20)]
                         )
    async def command(self, ctx: interactions.CommandContext, nazwa_komendy: int):

        command_name = nazwa_komendy
        raw = ('ic_tutorial', 'ic_commands', 'ic_info_command', 'ic_info_country', 'ic_map', 'ic_inventory_list',
               'ic_inventory_item', 'ic_inventory_give', 'ic_army_list', 'ic_army_templates', 'ic_army_recruit',
               'ic_army_disband', 'ic_army_reorg', 'ic_army_reinforce', 'ic_army_rename', 'ic_army_move',
               'ic_army_orders', 'ic_building_list', 'ic_building_templates', 'ic_building_build',
               'ic_building_destroy', 'ic_building_upgrade', 'ic_province_list', 'ic_province_rename')
        pages = []
        for element in raw:
            temp = getattr(models, element)
            pages.append(Page(embeds=temp()))

        await Paginator(
            client=self.bot,
            ctx=ctx,
            author_only=True,
            timeout=600,
            message="test",
            index=command_name,
            pages=pages
        ).run()

    @info.subcommand(description="Informacje o krajach.")
    @interactions.option(name='kraj', description='Wpisz dokładną nazwę kraju lub zpinguj gracza.', required=True)
    async def country(self, ctx: interactions.CommandContext, kraj: str):

        country = kraj
        st = time.time()
        connection = db.pax_engine.connect()
        if country.startswith('<@') and country.endswith('>'):  # if a ping
            # id = country[2:-1]
            country_id = connection.execute(text(
                f'SELECT country_id FROM players NATURAL JOIN countries WHERE player_id = {country[2:-1]}')).fetchone()
            if country_id is None:
                await ctx.send(f'Państwo - {country} - nie istnieje.')
                connection.close()
                return
        else:  # If string is (hopefully) a country name.
            country_id = None
            if '"' in country:
                pass
            else:
                country_id = connection.execute(
                    text(f'SELECT country_id FROM players NATURAL JOIN countries WHERE country_name = "{country}"'
                         )).fetchone()
            if country_id is None:
                await ctx.send(f'Państwo - {country} - nie istnieje.')
                connection.close()
                return

        et = time.time()
        print(et-st)

        query = db.pax_engine.connect().execute(text(
            f'SELECT COUNT(*) FROM countries WHERE NOT country_id BETWEEN 253 AND 255')).fetchone()
        pages = []
        for x in range(int(query[0])):
            embed = await models.build_country_embed(self, x + 1)
            print(str(x+1))
            pages.append(Page(embeds=embed))
        print(country_id)
        await Paginator(
            client=self.bot,
            ctx=ctx,
            author_only=True,
            timeout=300,
            message="test",
            index=country_id[0]-1,
            pages=pages
        ).run()
