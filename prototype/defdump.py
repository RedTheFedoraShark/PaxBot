import sys
from config.colorful import Colorful, timestamp
import cogs.__init__


async def load_extensions(bot):
    print(timestamp() + Colorful.CBLUE + "Loading extensions..." + Colorful.CEND)
    loaded = 0
    for ext in cogs.__init__.__all__:
        print(ext)
    """
    for module in sys.modules.values():
        if module.__name__.startswith('cogs.'):
            print(timestamp() + Colorful.CBLUE + 'MODULE:\t', Colorful.CGREEN + module.__name__ + Colorful.CEND)
            # for cls in map(module.__dict__.get, module.__all__):
            try:
                ext = module.__name__.split(".")
                await bot.load(ext[0])
                print(timestamp() + Colorful.CBLUE + 'ADDING:\t', Colorful.CGREEN + ext[0].__name__ + Colorful.CEND)
                loaded += 1
            except:
                print(timestamp() + Colorful.CREDBG + "An error occurred. Extension likely already loaded or missing." + Colorful.CEND)

    print(timestamp() + Colorful.CBLUE + str(loaded) + " extensions loaded!" + Colorful.CEND)
    """

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