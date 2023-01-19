import sys
from config.colorful import Colorful, timestamp
import cogs.__init__


def load_extensions(bot):
    print(timestamp() + Colorful.CBLUE + "Loading extensions..." + Colorful.CEND)
    loaded = 0
    #bot.load("cogs.template")
    for module in cogs.__init__.__all__:
        #try:
            bot.load('cogs.' + module)
            print(timestamp() + Colorful.CBLUE + 'ADDING:\t', Colorful.CGREEN + module + Colorful.CEND)
            loaded += 1


    print(timestamp() + Colorful.CBLUE + str(loaded) + " extensions loaded!" + Colorful.CEND)


# rewrite that later
async def unload_extensions(bot):
    coglist = [cog for cog in bot.cogs]
    print(timestamp() + Colorful.CBLUE + "Removing cogs...")
    removed = 0
    try:
        for cog in coglist:
            print(timestamp() + Colorful.CBLUE + "REMOVING:", Colorful.CGREEN + str(cog) + Colorful.CEND)
            await bot.remove_cog(cog)
            removed += 1
    except:
        print(timestamp() + Colorful.CREDBG + Colorful.CWHITE + "Something went terribly wrong!")
    print(timestamp() + Colorful.CBLUE + str(removed) + " cogs removed!" + Colorful.CEND)


async def print_extensions(bot):
    for ext in bot._extensions:
        print(ext)