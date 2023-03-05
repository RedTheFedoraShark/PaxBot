import interactions
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
import json
from sqlalchemy import create_engine, text

with open("./config/token.json") as f:
    t = json.load(f)


def setup(bot):
    Map(bot)


class Map(interactions.Extension):

    def __init__(self, bot):
        self.bot = bot

    @interactions.extension_command(description='Zapytaj kartografa o mapy.', scope='1015648339070558380')
    @interactions.option(name='mapa', description='Jaka mapa?',
                         choices=[interactions.Choice(name="Prowincji", value="provinces"),
                                  interactions.Choice(name="Regionów", value="regions"),
                                  interactions.Choice(name="Polityczna", value="countries"),
                                  interactions.Choice(name="Terenów", value="terrains"),
                                  interactions.Choice(name="Zasobów", value="goods")]
                         )
    @interactions.option(name='kontury', description='Dodać kontury prowincji?',
                         choices=[interactions.Choice(name="Tak", value="yes"),
                                  interactions.Choice(name="Nie", value="no")]
                         )
    async def mapa(self, ctx: interactions.CommandContext, map_type: str, borders: str):
        # Creating the SQLAlchemy for later.
        engine = create_engine(f"mysql+pymysql://{t['Muser']}:{t['Mpassword']}@{t['Mip']}/{t['Mdb']}?charset=utf8mb4",
                               pool_size=50, max_overflow=20)
        # PaxBot is thinking...
        await ctx.defer()
        if map_type == "provinces":
            final_image = Image(filename="maps/provinces.png")
            fi = final_image.clone()
            title = "Mapa Prowincji"
        elif map_type == "regions":
            final_image = Image(filename="maps/regions.png")
            fi = final_image.clone()
            title = "Mapa Regionów"
        else:
            await ctx.send("nie działa")

        if borders == "no":
            pass
        elif borders == "yes":
            first_layer = Image(filename="maps/borders.png")
            fl = first_layer.clone()
            with Drawing() as draw:
                draw.composite(operator="atop", left=0, top=0, width=fl.width, height=fl.height, image=fl)
                draw(fi)

        fi.save(filename="maps/final_image.png")
        file = interactions.File("maps/final_image.png")
        embed = interactions.Embed(
            title=title
        )
        # Using the file as an url, otherwise it can't be sent in an embed message.
        embed.set_image(url="attachment://final_image.png")
        await ctx.send(embeds=embed, files=file)
