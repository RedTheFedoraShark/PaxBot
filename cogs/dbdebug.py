import interactions
from prototype import defdump
from config.colorful import Colorful, timestamp
from database import *
from sqlalchemy import text

# from os import path
# import json


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
