import sys
from config.colorful import Colorful, timestamp


async def load_cogs(bot):
    print(timestamp() + Colorful.CBLUE + "Loading cogs..." + Colorful.CEND)
    loaded = 0
    for module in sys.modules.values():
        if module.__name__.startswith('cogs.'):
            print(timestamp() + Colorful.CBLUE + 'MODULE:\t', Colorful.CGREEN + module.__name__ + Colorful.CEND)
            for cls in map(module.__dict__.get, module.__all__):
                try:
                    await bot.add_cog(cls(bot))
                    print(timestamp() + Colorful.CBLUE + 'ADDING:\t', Colorful.CGREEN + cls.__name__ + Colorful.CEND)
                    loaded += 1
                except:
                    print(timestamp() + Colorful.CREDBG + "An error occurred. Cog likely in place or missing." + Colorful.CEND)

    print(timestamp() + Colorful.CBLUE + str(loaded) + " cogs loaded!" + Colorful.CEND)



async def unload_cogs(bot):
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


async def print_cogs(bot):
    for cog in bot.cogs:
        print(cog)