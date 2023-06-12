import interactions
from sqlalchemy import text
from database import *

# all class names from this file have to be included in def below
def setup(bot):
    Army(bot)


class Army(interactions.Extension):
    # constructor
    def __init__(self, bot):
        self.bot = bot

    @interactions.extension_command(
        description="manage armies"
    )
    async def army(self, ctx: interactions.CommandContext):
        return

    @army.subcommand(
        description="List armies"
    )
    async def list(self, ctx: interactions.CommandContext, target: str=None, admin: bool = False):
        connection = db.pax_engine.connect()
        original_input = target
        MODE = 'country'
        if target is None:
            target = connection.execute(
                text(f'SELECT country_id FROM players WHERE player_id = {ctx.author.id};')).fetchone()[0]
        else:
            target = target.strip()

            if target.startswith('<@') and target.endswith('>'):
                target = connection.execute(
                    text(f'SELECT country_id FROM players WHERE player_id = {target[2:-1]};')).fetchone()[0]
            elif target.startswith('#'):
                MODE = 'province'
                # select from borders twice, zip and check if the proince is seen by the player
                # visible
            else:
                pass

        if target == None:
            await ctx.send(f'There is no such {MODE} as "{original_input}".')
            return


        connection.close()
        return

    @army.subcommand(
        description="move"
    )
    async def disband(self, ctx: interactions.CommandContext):
        pass

    @army.subcommand(
        description=""
    )
    async def reorg(self, ctx: interactions.CommandContext):
        pass

    @army.subcommand(
        description=""
    )
    async def rename(self, ctx: interactions.CommandContext):
        pass

    @army.subcommand(
        description=""
    )
    async def recruit(self, ctx: interactions.CommandContext):
        pass

    @army.subcommand(
        description=""
    )
    async def templates(self, ctx: interactions.CommandContext):
        pass

    @army.subcommand(
        description=""
    )
    async def orders(self, ctx: interactions.CommandContext):
        pass

