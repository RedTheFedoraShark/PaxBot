import time

import interactions
import json
import numpy as np
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
from sqlalchemy import text
from database import *

with open("./config/token.json") as f:
    t = json.load(f)


def setup(bot):
    Map(bot)


class Map(interactions.Extension):

    def __init__(self, bot):
        self.bot = bot

    @interactions.extension_command(description='Zapytaj kartografa o mapy.', scope='917078941213261914')
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
                                  interactions.Choice(name="Nazwy Państw", value="country_name"),
                                  interactions.Choice(name="Armie", value="army")]
                         )
    @interactions.option(name='legenda', description='Jaką legendę chcesz?',
                         choices=[interactions.Choice(name="Żadna", value="none"),
                                  interactions.Choice(name="dummy", value="dummy")]
                         )
    @interactions.option(name='admin', description='Jesteś admin?')
    async def map(self, ctx: interactions.CommandContext,
                  map_type: str, borders: str, information: str, legend: str, admin: str = ''):  # legend: str
        # START THE CLOCK
        st = time.time()
        # PaxBot is thinking...
        await ctx.defer()
        title = ""

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
                result = db.pax_engine.connect().execute(text(
                    "SELECT pixel_capital_x, pixel_capital_y, country_id FROM provinces"))
                table = result.fetchall()
                result = db.pax_engine.connect().execute(text(
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
                final_image = Image(filename="maps/provinces.png")
                fi = final_image.clone()
                result = db.pax_engine.connect().execute(text(
                    "SELECT pixel_capital_x, pixel_capital_y, religion_color FROM provinces NATURAL JOIN religions"))
                final_table = result.fetchall()
                with Drawing() as draw:
                    for row in final_table:
                        draw.fill_color = Color(f'#{row[2]}')
                        draw.color(row[0], row[1], 'replace')
                    draw(fi)
                title = "Mapa Religii"
            case "pops":
                final_image = Image(filename="maps/regions.png")
                fi = final_image.clone()
                title = "Mapa Populacji"
            case "autonomy":
                final_image = Image(filename="maps/plain.png")
                image = Image(filename="maps/provinces.png")
                fi = final_image.clone()
                fi_2 = image.clone()
                result = db.pax_engine.connect().execute(text(
                    "SELECT pixel_capital_x, pixel_capital_y, province_autonomy, country_id FROM provinces"))
                final_table = result.fetchall()
                with Drawing() as draw:
                    for row in final_table:
                        match row[3]:
                            case 253 | 254 | 255:
                                draw.fill_color = Color(f'#00000000')
                                draw.color(row[0], row[1], 'replace')
                            case _:
                                r = hex(int(255-(row[2]*2.5)))
                                g = hex(int(0 + (row[2] * 2.5)))
                                draw.fill_color = Color(f'#{str(r)[2:]}{str(g)[2:]}00')
                                draw.color(row[0], row[1], 'replace')
                    draw(fi_2)
                with Drawing() as draw:
                    draw.composite(operator="atop", left=0, top=0, width=fi_2.width, height=fi_2.height, image=fi_2)
                    draw(fi)
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
                table = db.pax_engine.connect().execute(text(
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
                        province_text = row[0].replace(' ', '\n')
                        draw.text(row[1]*2, row[2]*2, f"{province_text}")
                    draw(fi)
                title = f"{title}, z nazwami prowincji."
            case "region_name":
                result = db.pax_engine.connect().execute(text(
                    f"SELECT region_name, region_x, region_y FROM regions WHERE NOT region_id='30'"))
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
                final_table = []
                result = db.pax_engine.connect().execute(text(
                    f"SELECT country_name, pixel_capital_x, pixel_capital_y, province_id, country_capital "
                    f"FROM countries LEFT JOIN provinces ON (countries.country_id=provinces.country_id)"
                    f"WHERE NOT country_capital='321'"))
                table = result.fetchall()
                for x in table:
                    if x[3] == x[4]:
                        final_table.append(x)
                    else:
                        pass
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
                title = f"{title}, z nazwami państw."
            case "army":
                fi.resize(3256, 3256)
                province_vison = []
                # Getting vision (only provinces for now)
                if admin == "admin":
                    if 917544661588004875 in ctx.author.roles:
                        print("Admin")
                        for i in range(321):
                            province_vison.append(i+1)
                        province_vison = str(province_vison).replace('[', '(').replace(']', ')')
                    else:
                        print("Chuj nie admin")
                        await ctx.send("Chuj nie admin.")
                        return
                else:
                    author_id = db.pax_engine.connect().execute(text(
                        f"SELECT country_id FROM players WHERE player_id = {ctx.author.id}")).fetchone()
                    result = db.pax_engine.connect().execute(text(
                        f"SELECT province_id FROM provinces WHERE country_id = {author_id[0]}")).fetchall()
                    result2 = db.pax_engine.connect().execute(text(
                        f"SELECT province_id, province_id_2 FROM borders")).fetchall()
                    table = []
                    for x in result:
                        table.append(x[0])
                    for line in result2:
                        if line[0] in table or line[1] in table:
                            province_vison.append(line)
                    # ADD UNIT VISION HERE #
                    # ADD UNIT VISION HERE #
                    # ADD UNIT VISION HERE #
                    province_vison = {x for ln in province_vison for x in ln}
                    province_vison = str(province_vison).replace('{', '(').replace('}', ')')
                print(province_vison)
                # Getting the things you actually see
                table = db.pax_engine.connect().execute(text(
                    f"SELECT army_strenght, manpower, army_visible, "
                    f"armies.country_id, pixel_capital_x, pixel_capital_y, armies.province_id FROM armies "
                    f"NATURAL JOIN units_cost LEFT JOIN provinces ON armies.province_id = provinces.province_id "
                    f"WHERE provinces.province_id in {province_vison}")).fetchall()
                print(table)
                # Merging units of the same country in the same province
                result = []
                for row in table:
                    manpower = 0
                    strenght = 0
                    units = 0
                    for row2 in table:
                        if row[6] == row2[6] and row[3] == row2[3]:
                            strenght += int(row2[0])
                            manpower += int(row2[1] * (row2[0] / 100))
                            units += 1
                    if units >= 1:
                        temp_row = (int(strenght/units), manpower, row[2], row[3], row[4], row[5])
                        if temp_row not in result:
                            result.append(temp_row)
                print(result)
                # Finally drawing this piece of shit onto the canvas.
                frame = Image(filename="maps/army/frame.png")
                fr = frame.clone()
                with Drawing() as draw:
                    draw.font = 'Times New Roman'
                    draw.font_size = 18
                    draw.stroke_width = 0
                    draw.text_alignment = 'center'
                    for row in result:
                        banner = Image(filename=f"maps/army/{row[3]}.png")
                        bn = banner.clone()
                        draw.fill_color = Color('green')
                        draw.rectangle(left=row[4] * 2 + 32, right=row[4] * 2 + 36,
                                       top=row[5] * 2 - 10, bottom=row[5] * 2 + 10)
                        draw.fill_color = Color('red')
                        draw.rectangle(left=row[4] * 2 + 32, right=row[4] * 2 + 36,
                                       top=row[5] * 2 - 11, bottom=row[5] * 2 - 11 - (int(row[0] / 5) - 20))
                        draw.composite(operator="atop", left=row[4] * 2 - 37, top=row[5] * 2 - 10, width=bn.width,
                                       height=bn.height, image=bn)
                        draw.composite(operator="atop", left=row[4] * 2 - 40, top=row[5] * 2 - 13, width=fr.width,
                                       height=fr.height, image=fr)
                        draw.fill_color = Color('white')
                        if row[1] >= 10000:
                            draw.text(row[4] * 2 + 7, row[5] * 2 + 7, f"{row[1] / 1000}k")
                        else:
                            draw.text(row[4] * 2 + 7, row[5] * 2 + 7, f"{row[1]}")
                    draw(fi)

                title = f"{title}, z armiami."

        match legend:
            case "none":
                pass
            case "dummy":
                dummy = "dummy"
        # STOP THE CLOCK
        et = time.time()
        elapsed_time = et - st
        print(str(elapsed_time)[0:5])
        fi.save(filename="maps/final_image.png")
        file = interactions.File("maps/final_image.png")
        embed_footer = interactions.EmbedFooter(
            text=f"{(str(elapsed_time)[0:5])}s",
            icon_url="https://i.imgur.com/K202lGe.png"
        )
        embed = interactions.Embed(
            title=title,
            footer=embed_footer
        )
        # Using the file as an url, otherwise it can't be sent in an embed message.
        embed.set_image(url="attachment://final_image.png")
        await ctx.send(embeds=embed, files=file)
