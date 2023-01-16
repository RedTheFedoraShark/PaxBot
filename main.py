import discord, json
from discord.ext import commands
from cogs import *
from prototype import *
from config.colorful import Colorful, timestamp
with open("./config/config.json") as f:
    config = json.load(f)
with open("./config/token.json") as f:
    token = json.load(f)

"""Declare intents for bot"""
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

"""Declare bot and add all cogs"""
bot = commands.Bot(command_prefix=config['Prefix'], intents=intents)


@bot.event
async def on_ready():
    await defdump.load_cogs(bot)
    print(timestamp() +
          Colorful.CVIOLET + str(bot.user) + ": " + Colorful.CBLUE + Colorful.CITALIC + "Ready to roll!" + Colorful.CEND)

    print(timestamp() + Colorful.CBLUE + "Connected to guilds:" + Colorful.CEND)
    for guild in bot.guilds:
        print(timestamp() + Colorful.CVIOLET + str(guild.id) + "\t" + Colorful.CBLUE + guild.name + Colorful.CEND)


@bot.event
async def on_command(ctx):
    print(timestamp() +
          Colorful.CVIOLET + str(ctx.author) +
          " ["+ str(ctx.author.id) +"] " +
          Colorful.CBLUE + " called " +
          Colorful.CVIOLET + str(ctx.command) +
          Colorful.CEND)


bot.run(token['Token'])

print("I am dead")
