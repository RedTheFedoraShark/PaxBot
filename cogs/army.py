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
        name="army",
        description="manage armies"
        # options=[
        #     interactions.Option(
        #         name="list",
        #         description="List armies (army) and details",
        #         type=interactions.OptionType(1)
        #     ),
        #
        #     interactions.Option(
        #         name="merge",
        #         description="Merge a few armies together",
        #         type=interactions.OptionType(1)
        #     ),
        #
        #     interactions.Option(
        #         name="split",
        #         description="Merge a few armies together",
        #         type=interactions.OptionType(1)
        #     ),
        #
        #     interactions.Option(
        #         name="move",
        #         description="Merge a few armies together",
        #         type=interactions.OptionType(1)
        #     )
        # ]
    )
    async def army(self, ctx: interactions.CommandContext):
        return

    @army.subcommand(
        description="aa",
        options=[
            interactions.Option(
                name='mode',
                description='What would you like to list?',
                type=interactions.OptionType.STRING,
                required=True
            ),
            interactions.Option(
                name='province',
                description='wow do you really need it?',
                type=interactions.OptionType.STRING,
                required=False
            )
        ]
    )
    async def list(self, ctx: interactions.CommandContext, mode: str, province=None):
        connection = db.pax_engine.connect()
        match mode:
            case 'owned':
                pass
            case 'province':
                pass
            case _:
                await ctx.send('Mode selected does not exist!')
        connection.close()
        return

    @army.subcommand(
        name='dump',
        description='!ADMIN ONLY! Dump all the armies into chat',
        options=[
            interactions.Option(
                name='province',
                description='wow do you really need it?',
                type=interactions.OptionType.INTEGER,
                required=False
            )
        ]
    )
    async def dump(self, ctx: interactions.CommandContext, province=None):
        connection = db.pax_engine.connect()
        if not await ctx.author.has_permissions(interactions.Permissions.ADMINISTRATOR):
            await ctx.send('You have insufficient permissions to run this command')
            connection.close()
            return

        if province is not None:
            query = 'SELECT * FROM armies WHERE province_id = province;'
        else:
            query = 'SELECT * FROM armies WHERE 1;'

        result = connection.execute(text(query)).fetchall()
        await ctx.send(f'{result}')
        connection.close()
        return


