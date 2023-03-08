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

    @interactions.extension_command(description='Zapytaj kartografa o mapy.') #, scope='1015648339070558380'
    @interactions.option(name='mapa', description='Jaka mapa?',
                         choices=[interactions.Choice(name="Prowincji", value="provinces"),
                                  interactions.Choice(name="Regionów", value="regions"),
                                  interactions.Choice(name="Terenów", value="terrains"),
                                  interactions.Choice(name="Zasobów", value="goods"),
                                  interactions.Choice(name="Polityczna", value="countries"),
                                  interactions.Choice(name="Religii", value="religions"),
                                  interactions.Choice(name="Populacji", value="pops"),
                                  interactions.Choice(name="Autonomii", value="autonomy")]
                         )
    @interactions.option(name='kontury', description='Dodać kontury prowincji?',
                         choices=[interactions.Choice(name="Nie", value="no"),
                                  interactions.Choice(name="Tak", value="yes")]
                         )
    @interactions.option(name='adnotacje', description='Jakie informacje chcesz?',
                         choices=[interactions.Choice(name="Żadne", value="none"),
                                  interactions.Choice(name="ID Prowincji", value="province_id"),
                                  interactions.Choice(name="Nazwy Prowincji", value="province_name"),
                                  interactions.Choice(name="Nazwy Regionów", value="region_name"),
                                  interactions.Choice(name="Nazwy Państw", value="country_name")]
                         )
    async def mapa(self, ctx: interactions.CommandContext, map_type: str, borders: str, information: str):
        # Creating the SQLAlchemy for later.
        engine = create_engine(f"mysql+pymysql://{t['Muser']}:{t['Mpassword']}@{t['Mip']}/{t['Mdb']}?charset=utf8mb4",
                               pool_size=50, max_overflow=20)
        # PaxBot is thinking...
        await ctx.defer()

        match map_type:
            case "provinces":
                final_image = Image(filename="maps/provinces.png")
                fi = final_image.clone()
                title = "Mapa Prowincji"
            case "regions":
                final_image = Image(filename="maps/regions.png")
                fi = final_image.clone()
                title = "Mapa Regionów"
            case "terrains":
                final_image = Image(filename="maps/regions.png")
                fi = final_image.clone()
                title = "Mapa Terenów"
            case "goods":
                final_image = Image(filename="maps/regions.png")
                fi = final_image.clone()
                title = "Mapa Zasobów"
            case "countries":
                final_image = Image(filename="maps/provinces.png")
                fi = final_image.clone()
                final_table = []
                result = engine.connect().execute(text(
                                                "SELECT pixel_capital_x, pixel_capital_y, country_id FROM provinces"))
                table = result.fetchall()
                for row in table:
                    result = engine.connect().execute(text(
                                                f"SELECT country_color FROM countries WHERE country_id = '{row[2]}'"))
                    entry = result.fetchall()
                    final = row[0], row[1], entry[0][0]
                    final_table.append(final)
                with Drawing() as draw:
                    for row in final_table:
                        draw.fill_color = Color(f'#{row[2]}')
                        draw.color(row[0], row[1], 'replace')
                    draw(fi)
                title = "Mapa Polityczna"
            case "religions":
                final_image = Image(filename="maps/regions.png")
                fi = final_image.clone()
                title = "Mapa Religii"
            case "pops":
                final_image = Image(filename="maps/regions.png")
                fi = final_image.clone()
                title = "Mapa Populacji"
            case "autonomy":
                final_image = Image(filename="maps/regions.png")
                fi = final_image.clone()
                title = "Mapa Autonomii"

        match borders:
            case "no":
                pass
            case "yes":
                title = f"{title} (kontury)"
                first_layer = Image(filename="maps/borders.png")
                fl = first_layer.clone()
                with Drawing() as draw:
                    draw.composite(operator="atop", left=0, top=0, width=fl.width, height=fl.height, image=fl)
                    draw(fi)

        match information:
            case "none":
                pass
            case "province_id":
                dummy = "dummy"
            case "province_name":
                dummy = "dummy"
            case "region_name":
                dummy = "dummy"
            case "country_name":
                dummy = "dummy"

        fi.save(filename="maps/final_image.png")
        file = interactions.File("maps/final_image.png")
        embed = interactions.Embed(
            title=title
        )
        # Using the file as an url, otherwise it can't be sent in an embed message.
        embed.set_image(url="attachment://final_image.png")
        await ctx.send(embeds=embed, files=file)
