import time

import interactions
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
from sqlalchemy import text
from database import *
import json
import asyncio

with open("./config/config.json") as f:
    configure = json.load(f)


def setup(bot):
    Map(bot)


def draw_army(draw, fr, row: tuple, y: int):
    draw.push()
    banner = Image(filename=f"gfx/army/{row[3]}.png")
    bn = banner.clone()
    draw.fill_color = Color('green')
    draw.rectangle(left=row[4] * 2 + 32, right=row[4] * 2 + 36,
                   top=row[5] * 2 - 10 + y, bottom=row[5] * 2 + 10 + y)
    draw.fill_color = Color('red')
    draw.rectangle(left=row[4] * 2 + 32, right=row[4] * 2 + 36,
                   top=row[5] * 2 - 11 + y, bottom=row[5] * 2 - 11 - (int(row[0] / 5) - 20) + y)
    draw.composite(operator="atop", left=row[4] * 2 - 37, top=row[5] * 2 - 10 + y, width=bn.width,
                   height=bn.height, image=bn)
    draw.composite(operator="atop", left=row[4] * 2 - 40, top=row[5] * 2 - 13 + y, width=fr.width,
                   height=fr.height, image=fr)
    draw.fill_color = Color('white')
    if row[1] >= 10000:
        draw.text(row[4] * 2 + 7, row[5] * 2 + 7 + y, f"{row[1] / 1000}k")
    else:
        draw.text(row[4] * 2 + 7, row[5] * 2 + 7 + y, f"{row[1]}")
    draw.pop()


class Map(interactions.Extension):

    def __init__(self, bot):
        self.bot = bot

    @interactions.slash_command(description='Zapytaj kartografa o mapy.', scopes=[configure['GUILD']])
    @interactions.slash_option(name='mapa', description='Jaka mapa?',
                               opt_type=interactions.OptionType.STRING,
                               required=True,
                               choices=[interactions.SlashCommandChoice(name="Prowincji", value="provinces"),
                                        interactions.SlashCommandChoice(name="Regionów", value="regions"),
                                        interactions.SlashCommandChoice(name="Terenów", value="terrains"),
                                        interactions.SlashCommandChoice(name="Zasobów", value="goods"),
                                        interactions.SlashCommandChoice(name="Polityczna", value="countries"),
                                        interactions.SlashCommandChoice(name="Religii", value="religions"),
                                        interactions.SlashCommandChoice(name="Populacji", value="pops"),
                                        interactions.SlashCommandChoice(name="Pusta", value="empty")]
                               )
    @interactions.slash_option(name='kontury', description='Dodać kontury prowincji?',
                               opt_type=interactions.OptionType.STRING,
                               required=True,
                               choices=[interactions.SlashCommandChoice(name="Nie", value="no"),
                                        interactions.SlashCommandChoice(name="Tak", value="yes")]
                               )
    @interactions.slash_option(name='adnotacje', description='Jakie informacje chcesz?',
                               opt_type=interactions.OptionType.STRING,
                               required=True,
                               choices=[interactions.SlashCommandChoice(name="Żadne", value="none"),
                                        interactions.SlashCommandChoice(name="ID Prowincji", value="province_id"),
                                        interactions.SlashCommandChoice(name="Nazwy Prowincji", value="province_name"),
                                        interactions.SlashCommandChoice(name="Nazwy Regionów", value="region_name"),
                                        interactions.SlashCommandChoice(name="Nazwy Państw", value="country_name"),
                                        interactions.SlashCommandChoice(name="Armie", value="army")]
                               )
    @interactions.slash_option(name='admin', description='Jesteś admin?', opt_type=interactions.OptionType.BOOLEAN)
    async def map(self, ctx: interactions.SlashContext,
                  mapa: str, kontury: str, adnotacje: str, admin: bool = False):  # legend: str
        map_type, borders, information, admin = mapa, kontury, adnotacje, admin

        # START THE CLOCK
        st = time.time()
        # PaxBot is thinking...
        await ctx.defer()
        is_admin = ctx.author.has_permission(interactions.Permissions.ADMINISTRATOR)

        def map_thread():
            title = ""
            match map_type:
                case "provinces":
                    final_image = Image(filename="gfx/maps/provinces.png")
                    fi = final_image.clone()
                    title = "Mapa Prowincji"
                case "regions":
                    final_image = Image(filename="gfx/maps/regions.png")
                    fi = final_image.clone()
                    title = "Mapa Regionów"
                case "terrains":
                    final_image = Image(filename="gfx/maps/terrains.png")
                    fi = final_image.clone()
                    title = "Mapa Terenów"
                case "goods":

                    final_image = Image(filename="gfx/maps/plain.png")
                    final_image_2 = Image(filename="gfx/maps/provinces.png")
                    fi = final_image.clone()
                    fi_2 = final_image_2.clone()
                    author_id = db.pax_engine.connect().execute(text(
                        f"SELECT country_id FROM players WHERE player_id = {ctx.author.id}")).fetchone()
                    result = db.pax_engine.connect().execute(text(
                        f"SELECT pixel_capital_x, pixel_capital_y, item_color, country_id, good_id "
                        f"FROM provinces LEFT "
                        f"JOIN items ON good_id = item_id")).fetchall()
                    admin_bool = False
                    if admin and is_admin:
                        admin_bool = True
                    with Drawing() as draw:
                        for row in result:
                            if row[3] == author_id[0] or admin_bool:  # If owned/seen
                                if row[4] == 255:  # If land with no goods
                                    draw.fill_color = Color(f'#969696')
                                    draw.color(row[0], row[1], 'replace')
                                elif row[4] == 254:  # If sea
                                    draw.fill_color = Color(f'#446BA3')
                                    draw.color(row[0], row[1], 'replace')
                                elif row[4] == 253:  # If mountians
                                    draw.fill_color = Color(f'#000000')
                                    draw.color(row[0], row[1], 'replace')
                                else:  # If not any of the above, draw the trade good
                                    draw.fill_color = Color(f'#{row[2]}')
                                    draw.color(row[0], row[1], 'replace')
                            else:  # If not owned
                                draw.fill_color = Color(f'#00000080')
                                draw.color(row[0], row[1], 'replace')
                        draw(fi_2)
                    with Drawing() as draw:
                        draw.composite(operator="atop", left=0, top=0, width=fi_2.width, height=fi_2.height, image=fi_2)
                        draw(fi)
                    title = "Mapa Zasobów"
                case "countries":
                    final_image = Image(filename="gfx/maps/provinces_only.png")
                    cropped = Image(filename="gfx/maps/provinces_cropped.png")
                    mask = Image(filename="gfx/maps/occupation_cropped.png")
                    fi = final_image.clone()
                    cr = cropped.clone()
                    result = db.pax_engine.connect().execute(text(
                        "SELECT pixel_capital_x, pixel_capital_y, country_color "
                        "FROM provinces LEFT JOIN countries ON provinces.country_id=countries.country_id "
                        "WHERE province_id NOT BETWEEN 251 AND 321")).fetchall()
                    result2 = db.pax_engine.connect().execute(text(
                        "SELECT pixel_capital_x, pixel_capital_y, country_color "
                        "FROM provinces LEFT JOIN countries ON provinces.controller_id=countries.country_id "
                        "WHERE province_id NOT BETWEEN 251 AND 321")).fetchall()
                    with Drawing() as draw:
                        for row in result2:
                            draw.fill_color = Color(f'#{row[2]}')
                            draw.color(row[0], row[1], 'replace')
                        draw(cr)
                    cr.composite_channel("alpha", mask, "copy_opacity", 0, 0)
                    with Drawing() as draw:
                        for row in result:
                            draw.fill_color = Color(f'#{row[2]}')
                            draw.color(row[0], row[1], 'replace')
                        draw.composite(operator="atop", left=0, top=0, width=cr.width, height=cr.height, image=cr)
                        draw(fi)
                    title = "Mapa Polityczna"
                case "religions":
                    final_image = Image(filename="gfx/maps/provinces_only.png")
                    cropped = Image(filename="gfx/maps/provinces_cropped.png")
                    mask = Image(filename="gfx/maps/occupation_cropped.png")
                    fi = final_image.clone()
                    cr = cropped.clone()
                    result = db.pax_engine.connect().execute(text(
                        "SELECT pixel_capital_x, pixel_capital_y, religion_color FROM provinces NATURAL JOIN religions "
                        "WHERE province_id NOT BETWEEN 251 AND 321")).fetchall()
                    result2 = db.pax_engine.connect().execute(text(
                        "SELECT pixel_capital_x, pixel_capital_y, religion_color "
                        "FROM provinces LEFT JOIN countries ON provinces.controller_id=countries.country_id "
                        "LEFT JOIN religions ON countries.religion_id = religions.religion_id "
                        "WHERE province_id NOT BETWEEN 251 AND 321")).fetchall()
                    with Drawing() as draw:
                        for row in result2:
                            draw.fill_color = Color(f'#{row[2]}')
                            draw.color(row[0], row[1], 'replace')
                        draw(cr)
                    cr.composite_channel("alpha", mask, "copy_opacity", 0, 0)
                    with Drawing() as draw:
                        for row in result:
                            draw.fill_color = Color(f'#{row[2]}')
                            draw.color(row[0], row[1], 'replace')
                        draw.composite(operator="atop", left=0, top=0, width=cr.width, height=cr.height, image=cr)
                        draw(fi)
                    title = "Mapa Religii"
                case "pops":
                    final_image = Image(filename="gfx/maps/plain.png")
                    image = Image(filename="gfx/maps/provinces.png")
                    fi = final_image.clone()
                    fi_2 = image.clone()
                    result = db.pax_engine.connect().execute(text(
                        "SELECT pixel_capital_x, pixel_capital_y, province_pops, country_id FROM provinces"))
                    final_table = result.fetchall()
                    low_pop = final_table[0][2]
                    lar_pop = final_table[0][2]
                    for x in final_table:
                        if x[2] < low_pop:
                            low_pop = x[2]
                        if x[2] > lar_pop:
                            lar_pop = x[2]
                    diff = lar_pop - low_pop
                    clr = 255 / diff
                    with Drawing() as draw:
                        for row in final_table:
                            match row[3]:
                                case 253 | 254:
                                    draw.fill_color = Color(f'#00000000')
                                    draw.color(row[0], row[1], 'replace')
                                case _:
                                    r = int((254 - ((row[2] - low_pop) * clr)) / 2)
                                    g = int((1 + ((row[2] - low_pop) * clr)) / 2)
                                    print(r, g, diff, clr)
                                    draw.fill_color = Color(f'#{r:02x}{g:02x}00')
                                    draw.color(row[0], row[1], 'replace')
                        draw(fi_2)
                    with Drawing() as draw:
                        draw.composite(operator="atop", left=0, top=0, width=fi_2.width, height=fi_2.height, image=fi_2)
                        draw(fi)
                    title = "Mapa Populacji"
                case "empty":
                    final_image = Image(width=1628, height=1628, background=Color('transparent'))
                    fi = final_image.clone()
                    title = "Mapa Pusta"

            match borders:
                case "no":
                    pass
                case "yes":
                    first_layer = Image(filename="gfx/maps/borders.png")
                    fl = first_layer.clone()
                    with Drawing() as draw:
                        draw.composite(operator="atop", left=0, top=0, width=fl.width, height=fl.height, image=fl)
                        draw(fi)
                    title = f"{title} (kontury)"

            match information:
                case "none":
                    title = f"{title}."
                case "province_id":
                    first_layer = Image(filename="gfx/maps/province_id.png")
                    fl = first_layer.clone()
                    with Drawing() as draw:
                        draw.composite(operator="atop", left=0, top=0, width=fl.width, height=fl.height, image=fl)
                        draw(fi)
                    title = f"{title}, z ID prowincji."
                case "province_name":
                    fi.scale(3256, 3256)
                    f_size = 20
                    off = int(f_size / 2)
                    table = db.pax_engine.connect().execute(text(
                        "SELECT province_name, pixel_capital_x, pixel_capital_y FROM provinces"))
                    final_table = table.fetchall()
                    with Drawing() as draw:
                        draw.font = 'Times New Roman'
                        draw.font_size = f_size
                        draw.stroke_color = Color('black')
                        draw.stroke_width = 2
                        draw.text_alignment = 'center'
                        for row in final_table:
                            province_text = row[0].replace(' ', '\n')
                            draw.text(row[1] * 2, row[2] * 2 + off, f"{province_text}")
                        draw(fi)
                    with Drawing() as draw:
                        draw.font = 'Times New Roman'
                        draw.font_size = f_size
                        draw.fill_color = Color('white')
                        draw.text_alignment = 'center'
                        for row in final_table:
                            province_text = row[0].replace(' ', '\n')
                            draw.text(row[1] * 2, row[2] * 2 + off, f"{province_text}")
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
                    province_vision = []
                    # Getting vision
                    if admin == "admin" and is_admin:
                        admin_bool = True
                        for i in range(321):
                            province_vision.append(i + 1)
                        province_vision_list = province_vision
                        province_vision = str(province_vision).replace('[', '(').replace(']', ')')
                    else:
                        admin_bool = False
                        author_id = db.pax_engine.connect().execute(text(
                            f"SELECT country_id FROM players WHERE player_id = {ctx.author.id}")).fetchone()
                        result = db.pax_engine.connect().execute(text(
                            f"SELECT province_id FROM provinces WHERE country_id = {author_id[0]}")).fetchall()
                        result1 = db.pax_engine.connect().execute(text(
                            f"SELECT province_id, army_vision_range FROM armies WHERE country_id = {author_id[0]}")).fetchall()
                        result2 = db.pax_engine.connect().execute(text(
                            f"SELECT province_id, province_id_2 FROM borders")).fetchall()
                        # Making the vision of the player
                        # Unit vision range part one
                        for x in result1:
                            if x[1] == 2:
                                tup = x[0],
                                if tup not in result:
                                    result.append(tup)
                        # Add Borders
                        table = []
                        for x in result:
                            table.append(x[0])
                        for line in result2:
                            if line[0] in table or line[1] in table:
                                province_vision.append(line)
                        # Put the data into a set (remove duplicates)
                        province_vision = {x for ln in province_vision for x in ln}
                        # Unit vision range part two
                        for x in result1:
                            if x[1] == 1:
                                province_vision.add(x[0])
                        province_vision_list = province_vision
                        province_vision = str(province_vision).replace('{', '(').replace('}', ')')
                    # Getting the things you actually see
                    table = db.pax_engine.connect().execute(text(
                        f"SELECT army_strenght, item_quantity, army_visible, "
                        f"armies.country_id, pixel_capital_x, pixel_capital_y, armies.province_id FROM armies "
                        f"NATURAL JOIN units_cost LEFT JOIN provinces ON armies.province_id = provinces.province_id "
                        f"WHERE provinces.province_id IN {province_vision} AND item_id=3")).fetchall()
                    # Remove invisible units for the player
                    if not admin_bool:
                        new_table = []
                        for row in table:
                            if row[2] == 0 and row[3] != author_id[0]:
                                pass
                            else:
                                new_table.append(row)
                        table = new_table
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
                            temp_row = (int(strenght / units), manpower, row[2], row[3], row[4], row[5], row[6])
                            if temp_row not in result:
                                result.append(temp_row)
                    # Sort it into a list of lists of tuples, so multiple countries can stand on one province.
                    sorted_result = []
                    index = 1
                    for province_id in range(321):
                        temp = []
                        for row in result:
                            if not temp and row[6] != province_id:
                                pass
                            elif not temp and row[6] == province_id:
                                temp.append(tuple(row))
                            elif temp[0][3] != row[3] and row[6] == province_id:
                                temp.append(tuple(row))
                        if temp and tuple(temp) not in sorted_result:
                            sorted_result.append(tuple(temp))
                        index += 1
                    # Finally drawing this piece of shit onto the canvas.
                    frame = Image(filename="gfx/army/frame.png")
                    fr = frame.clone()
                    image = Image(filename="gfx/maps/provinces.png")
                    fi_2 = image.clone()
                    all_provinces = db.pax_engine.connect().execute(text(
                        f"SELECT province_id, pixel_capital_x, pixel_capital_y FROM provinces")).fetchall()
                    with Drawing() as draw:
                        for row in all_provinces:
                            if row[0] in province_vision_list:
                                draw.fill_color = Color(f'#00000000')
                                draw.color(row[1], row[2], 'replace')
                            else:
                                draw.fill_color = Color(f'#00000080')
                                draw.color(row[1], row[2], 'replace')
                        draw(fi_2)
                    with Drawing() as draw:
                        draw.composite(operator="atop", left=0, top=0, width=fi_2.width, height=fi_2.height, image=fi_2)
                        draw(fi)
                        fi.scale(3256, 3256)
                    with Drawing() as draw:
                        draw.font = 'Times New Roman'
                        draw.font_size = 18
                        draw.stroke_width = 0
                        draw.text_alignment = 'center'
                        for row in sorted_result:
                            match len(row):
                                case 1:
                                    draw_army(draw, fr, row[0], 0)
                                case 2:
                                    draw_army(draw, fr, row[0], -12)
                                    draw_army(draw, fr, row[1], 12)
                                case 3:
                                    draw_army(draw, fr, row[0], -22)
                                    draw_army(draw, fr, row[1], 0)
                                    draw_army(draw, fr, row[2], 22)
                        draw(fi)

                    title = f"{title}, z armiami."
            return title, fi

        done = await asyncio.gather(asyncio.to_thread(map_thread))
        title, fi = done[0]
        # STOP THE CLOCK
        et = time.time()
        elapsed_time = et - st
        fi.save(filename="gfx/maps/final_image.png")
        file = interactions.File("gfx/maps/final_image.png")
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
