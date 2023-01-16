from discord.ext import commands
from prototype import defdump
from config.colorful import Colorful, timestamp
# from os import path
# import json

__all__ = ['Debug']


class Debug(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def kill(self, ctx):
        if ctx.author.id == await self.bot.is_owner(ctx.author):
            print(timestamp() +
                  Colorful.CBLUE + "Good night.")
            await ctx.send("Good night.")
            # db.close()
            await self.bot.close()
        else:
            await ctx.message.reply("You have no power here!")
            print(timestamp() +
                  Colorful.CRED + "Unauthorized access attempt from " +
                  Colorful.CVIOLET + str(ctx.author.id) +
                  Colorful.CEND)
            return
        return

    @commands.command()
    async def reload(self, ctx):
        await defdump.unload_cogs(self.bot)
        await defdump.load_cogs(self.bot)
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