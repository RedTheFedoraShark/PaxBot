import interactions
from prototype import defdump
from config.colorful import Colorful, timestamp
from database import *
from sqlalchemy import text

# from os import path
# import json


def setup(bot):
    DBDebug(bot)


class DBDebug(interactions.Extension):
    def __init__(self, bot):
        self.bot = bot

    @interactions.extension_command(
        name="database",
        description="engine check"
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