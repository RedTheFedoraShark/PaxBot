import interactions


# all class names from this file have to be included in def below
def setup(bot):
    Template(bot)


class Template(interactions.Extension):
    # constructor
    def __init__(self, bot):
        self.bot = bot

    @interactions.slash_command(
        name="ping"
    )
    async def ping(self, ctx):
        await ctx.send("<:BetterGetKarl:1259091835167576064>")
