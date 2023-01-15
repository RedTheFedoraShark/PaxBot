from discord.ext import commands

# all class names from this file have to be included in __all__ array
__all__ = ['Template']


class Template(commands.Cog):
    # constructor
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.message.reply("Pong!")