import interactions
from interactions.ext.paginators import Page, Paginator
from database import *
from config import models
from sqlalchemy import text
import time
import json

with open("./config/config.json") as f:
    configure = json.load(f)


def setup(bot):
    Info(bot)


class Info(interactions.Extension):

    def __init__(self, bot):
        self.bot = bot

    @interactions.slash_command(description='Ściąga z komendami Pax Zeonica.', scopes=[configure['GUILD']])
    async def commands(self, ctx):
        await ctx.send(embeds=models.commands())

    @interactions.slash_command(description='Testuj', scopes=[configure['GUILD']])
    async def info(self, ctx: interactions.SlashContext):
        pass

    @info.subcommand(sub_cmd_description="Informacje o komendach.")
    @interactions.slash_option(name="nazwa_komendy", description='Wpisz nazwę komendy którą chcesz sprawdzić.',
                               required=True, opt_type=interactions.OptionType.INTEGER,
                               choices=[  # Information
                                   interactions.SlashCommandChoice(name="/tutorial", value=0),
                                   interactions.SlashCommandChoice(name="/commands", value=1),
                                   interactions.SlashCommandChoice(name="/info command", value=2),
                                   interactions.SlashCommandChoice(name="/info country", value=3),
                                   interactions.SlashCommandChoice(name="/map", value=4),
                                   # Inventory
                                   interactions.SlashCommandChoice(name="/inventory list", value=5),
                                   interactions.SlashCommandChoice(name="/inventory item", value=6),
                                   interactions.SlashCommandChoice(name="/inventory give", value=7),
                                   # Army
                                   interactions.SlashCommandChoice(name="/army list", value=8),
                                   interactions.SlashCommandChoice(name="/army templates", value=9),
                                   interactions.SlashCommandChoice(name="/army recruit", value=10),
                                   interactions.SlashCommandChoice(name="/army disband", value=11),
                                   interactions.SlashCommandChoice(name="/army reorg", value=12),
                                   interactions.SlashCommandChoice(name="/army reinforce", value=13),
                                   interactions.SlashCommandChoice(name="/army rename", value=14),
                                   interactions.SlashCommandChoice(name="/army move", value=15),
                                   interactions.SlashCommandChoice(name="/army orders", value=16),
                                   # Buildings
                                   interactions.SlashCommandChoice(name="/building list", value=17),
                                   interactions.SlashCommandChoice(name="/building templates", value=18),
                                   interactions.SlashCommandChoice(name="/building build", value=19),
                                   interactions.SlashCommandChoice(name="/building destroy", value=20),
                                   # Provinces
                                   interactions.SlashCommandChoice(name="/province list", value=21),
                                   interactions.SlashCommandChoice(name="/province rename", value=22)]
                               )
    async def command(self, ctx: interactions.SlashContext, nazwa_komendy: int):

        command_name = nazwa_komendy
        raw = ('ic_tutorial', 'ic_commands', 'ic_info_command', 'ic_info_country', 'ic_map', 'ic_inventory_list',
               'ic_inventory_item', 'ic_inventory_give', 'ic_army_list', 'ic_army_templates', 'ic_army_recruit',
               'ic_army_disband', 'ic_army_reorg', 'ic_army_reinforce', 'ic_army_rename', 'ic_army_move',
               'ic_army_orders', 'ic_building_list', 'ic_building_templates', 'ic_building_build',
               'ic_building_destroy', 'ic_province_list', 'ic_province_rename')
        pages = []
        for element in raw:
            pages.append(getattr(models, element)())

        # paginator = Paginator.create_from_string(ctx.client, "Test", page_size=1000)
        paginator = Paginator.create_from_embeds(ctx.client, *pages)
        paginator.page_index = nazwa_komendy
        await paginator.send(ctx=ctx)

    @info.subcommand(sub_cmd_description="Informacje o krajach.")
    @interactions.slash_option(name='kraj', description='Wpisz dokładną nazwę kraju lub zpinguj gracza.',
                               required=False, opt_type=interactions.OptionType.STRING)
    async def country(self, ctx: interactions.SlashContext, kraj: str = ''):

        country = kraj
        st = time.time()
        connection = db.pax_engine.connect()
        if country:
            if country.startswith('<@') and country.endswith('>'):  # if a ping
                # id = country[2:-1]
                country_id = connection.execute(text(
                    f'SELECT country_id FROM players NATURAL JOIN countries WHERE player_id = {country[2:-1]}')).fetchone()
                if country_id is None:
                    await ctx.send(f"```ansi\nGracz '{country}' \u001b[0;31mnie ma państwa\u001b[0;0m.")
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
                    await ctx.send(f"```ansi\nPaństwo '{country}' \u001b[0;31mnie istnieje\u001b[0;0m.")
                    connection.close()
                    return
        else:
            country_id = [1]

        et = time.time()
        print(et - st)

        query = db.pax_engine.connect().execute(text(
            f'SELECT COUNT(*) FROM countries WHERE NOT country_id BETWEEN 253 AND 255')).fetchone()
        pages = []
        for x in range(int(query[0])):
            embed = await models.build_country_embed(self, x + 1, )
            print(str(x + 1))
            pages.append(embed)
        print(country_id)
        print(pages)
        paginator = Paginator.create_from_embeds(ctx.client, *pages)
        paginator.page_index = country_id[0] - 1
        await paginator.send(ctx=ctx)
