import interactions
from prototype import defdump
from config.colorful import Colorful, timestamp
# from os import path
# import json


def setup(bot):
    Debug(bot)


class Debug(interactions.Extension):
    def __init__(self, bot):
        self.bot = bot

    @interactions.extension_command(
        name="kill",
        description="Turn off the bot",
        scope='917078941213261914'
    )
    async def kill(self, ctx):
        if self.bot.me.owner.id == ctx.author.id:
            print(timestamp() +
                  Colorful.CBLUE + "Good night.")
            await ctx.send("Good night.")
            # db.close()
            await self.bot._stop()
        else:
            await ctx.send("You have no power here!")
            print(timestamp() +
                  Colorful.CRED + "Unauthorized access attempt from " +
                  Colorful.CVIOLET + str(ctx.author.id) +
                  Colorful.CEND)
            return
        return

    @interactions.extension_command(
        scope='917078941213261914'
    )
    async def add(self, ctx: interactions.CommandContext):
        pass

    @add.subcommand(
    )
    async def template(self, ctx: interactions.CommandContext):
        pass

    @add.subcommand(
    )
    async def building(self, ctx: interactions.CommandContext):
        pass

    @add.subcommand(
    )
    async def tradegood(self, ctx: interactions.CommandContext):
        pass

    @add.subcommand(
    )
    async def item(self, ctx: interactions.CommandContext):
        pass
