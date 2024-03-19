import interactions
from prototype import defdump
from config.colorful import Colorful, timestamp
from database import *
from sqlalchemy import text
import numpy as np


# from os import path
# import json


def inventories_debug():
    connection = db.pax_engine.connect()
    countries = connection.execute(text(f"SELECT country_id FROM countries")).fetchall()
    items = connection.execute(text(f"SELECT item_id FROM items")).fetchall()
    countries = np.rot90(np.array(countries)).tolist()
    items = np.rot90(np.array(items)).tolist()
    countries = countries[0][:-3]
    items = items[0]
    values = []
    for c in countries:
        for i in items:
            values.append((i, c))
    values = str(values)[1:-1]
    print(items)
    print(countries)
    print(values)
    connection.execute(
        text(f"INSERT IGNORE INTO inventories (item_id, country_id) VALUES {values}")).connection.commit()
    return


def terrains_modifiers_debug():
    connection = db.pax_engine.connect()
    terrains = connection.execute(text(f"SELECT terrain_id FROM terrains")).fetchall()
    items = connection.execute(text(f"SELECT item_id FROM items")).fetchall()
    terrains = np.rot90(np.array(terrains)).tolist()
    items = np.rot90(np.array(items)).tolist()
    terrains = terrains[0]
    items = items[0]
    values = []
    for t in terrains:
        for i in items:
            values.append((i, t))
    values = str(values)[1:-1]
    print(items)
    print(terrains)
    print(values)
    connection.execute(
        text(f"INSERT IGNORE INTO terrains_modifiers (item_id, terrain_id) VALUES {values}")).connection.commit()
    return


class DBDebug(interactions.Extension):
    def __init__(self, bot):
        self.bot = bot

    @interactions.extension_command(
        name="debug",
        description="engine check",
        scope='917078941213261914'
    )
    async def debug(self, ctx):
        inventories_debug()
        terrains_modifiers_debug()
        await ctx.send("test")

    @interactions.extension_command(
        name="database",
        description="engine check",
        scope='917078941213261914'
    )
    async def database(self, ctx):
        embed = interactions.Embed(
            title="db debug"
        )
        if db.check_engine(db.pax_engine):
            embed.add_field(
                name='engine',
                value=':green_circle:connected'
            )
        else:
            embed.add_field(
                name='engine',
                value=':red_circle:not connected'
            )

        # Using the file as an url, otherwise it can't be sent in an embed message.
        await ctx.send(embeds=embed)
        return

    @interactions.extension_command(
        name="tabledump",
        description="show tables"
    )
    async def something(self, ctx):
        with db.pax_engine.connect() as connection:
            result = connection.execute(text('show tables;'))
        await ctx.send('{}'.format(result.all()))
        return

    @interactions.extension_command(
        name='backup',
        description='Make a database backup copy.'
    )
    async def backup(self, ctx: interactions.CommandContext):
        if not await ctx.author.has_permissions(interactions.Permissions.ADMINISTRATOR):
            await ctx.send("You have no power here!")

            return
        await ctx.send("Database backed up successfully!")
        db.backup()
        return

    @interactions.extension_command(
        name='test',
        description='kogoś srogo popierdoliło',
    )
    async def test(self, ctx: interactions.CommandContext):
        a = 1
        await ctx.send("jebać adama "+ str(a))
        a = 45
        await ctx.send("jebać adama "+ str(a))
        return


def setup(bot):
    DBDebug(bot)
