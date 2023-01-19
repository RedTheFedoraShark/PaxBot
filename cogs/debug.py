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
        description="Turn off the bot"
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




    """
    parentPath = path.abspath(path.dirname(path.curdir))
    with open(path.join(parentPath, "config/config.json")) as f:
        self.owner = int(json.load(f)['Owner'])
            
    @commands.command()
    async def reconnect(self, ctx):
        if ctx.author.guild_permissions.administrator:

            await ctx.send("Reconnecting...")
            print("Reconnecting...")
            await self.bot.connect()
        else:
            print("Unauthorized access attempt from {0}.".format(ctx.author.id))
            return
        return
    """