import interactions
import json
import math
import numpy as np
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
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
                                  interactions.Choice(name="Autonomii", value="autonomy"),
                                  interactions.Choice(name="Pusta", value="empty")]
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
    @interactions.option(name='legenda', description='Jaką legendę chcesz?',
                         choices=[interactions.Choice(name="Żadna", value="none"),
                                  interactions.Choice(name="dummy", value="dummy")]
                         )
    async def mapa(self, ctx: interactions.CommandContext, map_type: str, borders: str, information: str, legend: str):
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
                final_image = Image(filename="maps/terrains.png")
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
                result = engine.connect().execute(text(
                                                "SELECT country_color, country_id FROM countries"))
                table2 = result.fetchall()
                table2 = np.array(table2)
                for row in table:
                    index = np.where(table2 == np.str_(row[2]))
                    final = row[0], row[1], table2[index[0][0]][0]
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
            case "empty":
                final_image = Image(width=1628, height=1628, background=Color('transparent'))
                fi = final_image.clone()
                title = "Mapa Pusta"

        match borders:
            case "no":
                pass
            case "yes":
                first_layer = Image(filename="maps/borders.png")
                fl = first_layer.clone()
                with Drawing() as draw:
                    draw.composite(operator="atop", left=0, top=0, width=fl.width, height=fl.height, image=fl)
                    draw(fi)
                title = f"{title} (kontury)"

        match information:
            case "none":
                title = f"{title}."
            case "province_id":
                first_layer = Image(filename="maps/province_id.png")
                fl = first_layer.clone()
                with Drawing() as draw:
                    draw.composite(operator="atop", left=0, top=0, width=fl.width, height=fl.height, image=fl)
                    draw(fi)
                title = f"{title}, z ID prowincji."
            case "province_name":
                fi.resize(3256, 3256)
                table = engine.connect().execute(text(
                    "SELECT province_name, pixel_capital_x, pixel_capital_y FROM provinces"))
                final_table = table.fetchall()
                with Drawing() as draw:
                    draw.font = 'Times New Roman'
                    draw.font_size = 20
                    draw.stroke_color = Color('black')
                    draw.stroke_width = 2
                    draw.text_alignment = 'center'
                    for row in final_table:
                        province_text = row[0].replace(' ', '\n')
                        draw.text(row[1]*2, row[2]*2, f"{province_text}")
                    draw(fi)
                with Drawing() as draw:
                    draw.font = 'Times New Roman'
                    draw.font_size = 20
                    draw.fill_color = Color('white')
                    draw.text_alignment = 'center'
                    for row in final_table:
                        draw.text(row[1]*2, row[2]*2, f"{province_text}")
                    draw(fi)
                title = f"{title}, z nazwami prowincji."
            case "region_name":
                result = engine.connect().execute(text(
                    f"SELECT region_name, region_x, region_y FROM regions"))
                final_table = result.fetchall()
                with Drawing() as draw:
                    draw.font = 'Times New Roman'
                    draw.font_size = 40
                    draw.stroke_color = Color('black')
                    draw.stroke_width = 8
                    draw.text_alignment = 'center'
                    for row in final_table:
                        region_text = row[0].replace(' ', '\n')
                        draw.text(row[1], row[2], f"{region_text}")
                    draw.fill_color = Color('white')
                    draw.stroke_color = Color('white')
                    draw.stroke_width = 0
                    draw.text_alignment = 'center'
                    for row in final_table:
                        region_text = row[0].replace(' ', '\n')
                        draw.text(row[1], row[2], f"{region_text}")
                    draw(fi)
                title = f"{title}, z nazwami regionów."
            case "country_name":
                title = f"{title}, z nazwami państw."

        match legend:
            case "none":
                pass
            case "dummy":
                dummy = "dummy"

        fi.save(filename="maps/final_image.png")
        file = interactions.File("maps/final_image.png")
        embed = interactions.Embed(
            title=title
        )
        # Using the file as an url, otherwise it can't be sent in an embed message.
        embed.set_image(url="attachment://final_image.png")
        await ctx.send(embeds=embed, files=file)
