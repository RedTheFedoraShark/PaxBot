from discord.ext import commands
from prototype import defdump

# all class names from this file have to be included in __all__ array
__all__ = ['TurnTools']


class TurnTools(commands.Cog):
    # constructor
    def __init__(self, bot):
        self.bot = bot

    def income(self):
        pass

    def movement(self):
        pass

    @commands.command(aliases=['endturn'])
    async def next_turn(self, ctx):
        pass
        await defdump.unload_cogs(self.bot)
        """
        Rest of code in here
        """
        await defdump.load_cogs(self.bot)
