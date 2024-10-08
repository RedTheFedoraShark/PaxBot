import json
import logging

import interactions
from cogs import *
from prototype import *
from config.colorful import Colorful, timestamp
with open("./config/config.json") as f:
    configure = json.load(f)

from database import *

"""Declare intents for bot"""
intents = interactions.Intents.DEFAULT
intents.messages = True
intents.message_content = True

"""Declare bot and add all cogs"""
# bot = commands.Bot(command_prefix=config['Prefix'], intents=intents)
bot = interactions.Client(token=configure['TOKEN'], intents=intents, logging=logging.INFO,)
                          #delete_unused_application_cmds=True)

bot.load_extension('interactions.ext.sentry',
                   dsn="https://3cdb51a1282cf049c4565735aad4d413@o4507509505458176."
                       "ingest.de.sentry.io/4507509639282768")
defdump.load_extensions(bot)


@bot.event
async def on_ready():
    print(timestamp() +
          Colorful.CVIOLET + str(bot.me.name) + ": " + Colorful.CBLUE + Colorful.CITALIC + "Ready to roll!" + Colorful.CEND)

    print(timestamp() + Colorful.CBLUE + "Connected to guilds:" + Colorful.CEND)
    for guild in bot.guilds:
        print(timestamp() + Colorful.CVIOLET + str(guild.id) + "\t" + Colorful.CBLUE + guild.name + Colorful.CEND)


@bot.event
async def on_command(ctx: interactions.SlashContext):
    try:
        options = f'{ctx.data.options[0].name}, {[f"{o.name}:{o.value}" for o in ctx.data.options[0].options]}'
        if ctx.data.options[0].name is not None:
            subcommand = ctx.data.options[0].name
        if ctx.data.options[0].options is not None:
            for o in ctx.data.options[0].options:
                options += f'{o.name}:{o.value}, '
    except TypeError:
        options = ''
        subcommand = ''
    print(timestamp() +
          Colorful.CVIOLET + str(ctx.author.name) +
          "[" + str(ctx.author.id) + "] " +
          Colorful.CBLUE + "called " +
          Colorful.CVIOLET + f'{ctx.data.name} {subcommand}' +
          Colorful.CBLUE + " with options: " +
          Colorful.CVIOLET + options +
          Colorful.CEND)

bot.start()

print(timestamp() + Colorful.CBLUE + "I am dead.")
