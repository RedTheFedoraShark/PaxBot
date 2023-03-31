import interactions
from config import models


def setup(bot):
    Commands(bot)


class Commands(interactions.Extension):

    def __init__(self, bot):
        self.bot = bot

    @interactions.extension_command(description='Testuj', scope='917078941213261914')
    async def commands(self, ctx):
        await ctx.send(embeds=models.commands())
