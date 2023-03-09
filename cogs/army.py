import interactions
from sqlalchemy import text
from database import *

# all class names from this file have to be included in def below
def setup(bot):
    Template(bot)


class Template(interactions.Extension):
    # constructor
    def __init__(self, bot):
        self.bot = bot

    @interactions.extension_command(
        name="army",
        description="manage armies",
        options=[
            interactions.Option(
                name="list",
                description="List armies (army) and details",
                type=interactions.OptionType.SUB_COMMAND
            ),

            interactions.Option(
                name="merge",
                description="Merge a few armies together",
                type=interactions.OptionType.SUB_COMMAND
            ),

            interactions.Option(
                name="split",
                description="Merge a few armies together",
                type=interactions.OptionType.SUB_COMMAND
            ),

            interactions.Option(
                name="move",
                description="Merge a few armies together",
                type=interactions.OptionType.SUB_COMMAND
            )
        ]
    )
    async def army(self, ctx: interactions.CommandContext, sub_command: str):
        connection = db.pax_engine.connect()
        country = connection.execute(
            text(f'SELECT country_id FROM players WHERE player_id = {ctx.author.id}')).fetchall()[0][0]

        match sub_command:
            case 'list':
                if ctx.author.has_permissions(8):
                    result = connection.execute(text('SELECT * FROM armies WHERE 1'))
                    pass
                else:
                    result = connection.execute(text('SELECT * FROM armies WHERE country_id = country;'))
                await ctx.send(f'{result.fetchall()}')
            case 'merge':
                pass
            case 'split':
                pass
            case 'move':
                pass
        connection.close()

    @army.subcommand(
        name="list2",
        description="",
        options=None
    )
    async def list2(self, ctx: interactions.CommandContext):
        connection = db.pax_engine.connect()
        country = connection.execute(
            text(f'SELECT country_id FROM players WHERE player_id = {ctx.author.id}')).fetchall()[0][0]

        if ctx.author.has_permissions(8):
            result = connection.execute(text('SELECT * FROM armies WHERE 1'))
            pass
        else:
            result = connection.execute(text('SELECT * FROM armies WHERE country_id = country;'))
        await ctx.send(f'{result.fetchall()}')
