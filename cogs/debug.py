import discord
from discord.ext import commands
from os import path
import json

__all__ = ['Debug']


class Debug(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        parentPath = path.abspath(path.dirname(path.curdir))
        with open(path.join(parentPath, "config/config.json")) as f:
            self.owner = int(json.load(f)['Owner'])

    @commands.command()
    async def ping(self, ctx):
        await ctx.message.reply("Pong!")
    """
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
    @commands.command()
    async def kill(self, ctx):
        if ctx.author.id == self.owner:
            print("Good night.")
            await ctx.send("Good night.")
            # db.close()
            await self.bot.close()
        else:
            print("Unauthorized access attempt from {0}.".format(ctx.author.id))
            return
        return
