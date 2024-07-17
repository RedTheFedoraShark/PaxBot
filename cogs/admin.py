import interactions
from sqlalchemy import text
from database import *
import pandas as pd
import numpy as np
from cogs import province


def setup(bot):
    Admin(bot)


class Admin(interactions.Extension):
    def __init__(self, bot):
        self.bot = bot

    @interactions.extension_command(description="Testuj", scope='917078941213261914')
    async def admin(self, ctx: interactions.CommandContext):
        return

