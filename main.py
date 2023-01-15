import discord, json, sys
from discord.ext import commands
from cogs import *
with open("./config/config.json") as f:
    config = json.load(f)


"""Declare intents for bot"""
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

"""Declare bot and add all cogs"""
bot = commands.Bot(command_prefix=config['Prefix'], intents=intents)


@bot.event
async def on_ready():
    #await bot.add_cog(debug.Debug(bot))
    print("Loading commands...")
    for module in sys.modules.values():
        if module.__name__.startswith('cogs.'):
            print('--------\nmodule:', module.__name__)
            for cls in map(module.__dict__.get, module.__all__):
                print('adding cog:', cls.__name__)
                try:
                    await bot.add_cog(cls(bot))
                except:
                    print("An error occurred. Cog likely in place or missing.")

    print("--------\nCommands loaded!")

    print("{} ready to roll!".format(bot.user))
    # print("{}".format(config['database']['user']))
    print("Connected to guilds:")
    for guild in bot.guilds:
        print(guild.id)


@bot.event
async def on_command_error():
    print("")

bot.run(config['Token'])

print("I am dead")
