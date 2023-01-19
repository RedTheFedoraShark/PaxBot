from discord.ext import commands
import interactions
# all class names from this file have to be included in __all__ array
__all__ = ['Template']


class Template(interactions.Extension):
    # constructor
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['check'])
    async def ping(self, ctx):
        await ctx.message.reply("Pong!")
