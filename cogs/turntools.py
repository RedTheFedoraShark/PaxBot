import dbm

import interactions
from prototype import defdump
from database import *
from sqlalchemy import text
# all class names from this file have to be included in __all__ array
__all__ = ['TurnTools']


class TurnTools(interactions.Extension):
    # constructor
    def __init__(self, bot):
        self.bot = bot

    async def migration(self):
        pass

    async def pop_growth(self):
        pass

    @interactions.extension_command()
    async def next_turn(self, ctx):
        await ctx.defer()
        # unload cogs so that players can't interrupt the calculations
        await defdump.unload_cogs(self.bot)

        connection = db.pax_engine



        connection.close()

        await defdump.load_cogs(self.bot)

