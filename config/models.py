import random
import pandas as pd
import interactions
from database import *
from sqlalchemy import text
from interactions.ext.paginator import Page


# Pagify a table string
async def pagify(dataframe: list):
    bit = ''
    bits = []
    for line in dataframe:
        if len(bit) > 1860:
            bits.append(bit)
            bit = ''
        bit = f"{bit}\n{line}"
    pages = []
    for i, bit in enumerate(bits):
        pages.append(Page(title=str(i+1) + ". Strona", content=f"```ansi\n{bit}```"))
    return pages


# /province list
async def build_province_list(country_id: int):
    connection = db.pax_engine.connect()
    table = connection.execute(text(
        f"SELECT province_name, province_id, region_name, terrain_name, good_name, religion_name, province_pops, "
        f"province_autonomy FROM provinces NATURAL JOIN regions NATURAL JOIN goods NATURAL JOIN terrains "
        f"NATURAL JOIN religions "
        f"WHERE country_id = {country_id} OR controller_id = {country_id}")).fetchall()

    df = pd.DataFrame(table, columns=[
        'Prowincja', 'ID', 'Region', 'Teren', 'Zasoby', 'Religia', 'Populacja', 'Autonomia'])
    df = df.sort_values(by=['ID'])
    for i, row in df.iterrows():
        df.at[i, 'ID'] = f"\u001b[0;30m ({df['ID'][i]})\u001b[0;0m"
        if df['Autonomia'][i] > 67:
            autonomia = f"\u001b[0;31m{df['Autonomia'][i]}%\u001b[0;0m"
        elif df['Autonomia'][i] < 33:
            autonomia = f"\u001b[0;32m{df['Autonomia'][i]}%\u001b[0;0m"
        else:
            autonomia = f"\u001b[0;33m{df['Autonomia'][i]}%\u001b[0;0m"
        df.at[i, 'Autonomia'] = autonomia
    combined = df['Prowincja'] + df['ID']
    df.drop(['Prowincja', 'ID'], axis=1, inplace=True)
    df.insert(0, 'Prowincja (ID)', combined)
    return df


async def build_province_list_admin():
    connection = db.pax_engine.connect()
    table = connection.execute(text(
        f"SELECT province_name, province_id, region_name, terrain_name, good_name, religion_name, province_pops, "
        f"province_autonomy FROM provinces NATURAL JOIN regions NATURAL JOIN goods NATURAL JOIN terrains "
        f"NATURAL JOIN religions")).fetchall()

    df = pd.DataFrame(table, columns=[
        'Prowincja', 'ID', 'Region', 'Teren', 'Zasoby', 'Religia', 'Populacja', 'Autonomia'])
    df = df.sort_values(by=['ID'])
    for i, row in df.iterrows():
        df.at[i, 'ID'] = f"\u001b[0;30m ({df['ID'][i]})\u001b[0;0m"
        if df['Autonomia'][i] > 67:
            autonomia = f"\u001b[0;31m{df['Autonomia'][i]}%\u001b[0;0m"
        elif df['Autonomia'][i] < 33:
            autonomia = f"\u001b[0;32m{df['Autonomia'][i]}%\u001b[0;0m"
        else:
            autonomia = f"\u001b[0;33m{df['Autonomia'][i]}%\u001b[0;0m"
        df.at[i, 'Autonomia'] = autonomia
    combined = df['Prowincja'] + df['ID']
    df.drop(['Prowincja', 'ID'], axis=1, inplace=True)
    df.insert(0, 'Prowincja (ID)', combined)
    return df


async def build_province_embed(province_id: int):
    connection = db.pax_engine.connect()
    query = connection.execute(text(
        f'SELECT * FROM provinces NATURAL JOIN countries NATURAL JOIN religions WHERE province_id = "{province_id}"'
    )).fetchall()
    # Repairing names for multiple players on one country
    #query = list(query[0])
    #query2 = connection.execute(text(
    #    f'SELECT SUM(province_pops), COUNT(*) FROM provinces WHERE country_id = "{country_id}"')).fetchone()
    ## Creating embed elements
    #embed_footer = interactions.EmbedFooter(
    #    text=query[13],
    #    icon_url=query[14]
    #)
    #embed_thumbnail = interactions.EmbedImageStruct(
    #    url=query[12]
    #)
    #embed_author = interactions.EmbedAuthor(
    #    name=query[3],
    #)

    # Building the Embed
    embed = interactions.Embed(
        #color=int(query[7], 16),
        title=str(province_id),
        # description=result_countries[5],
        #url=query[11],
        #footer=embed_footer,
        #thumbnail=embed_thumbnail,
        #author=embed_author,
        #fields=[f1, f2, fb, f3, f4, fb, f5, f6, fb, f7, f8]
    )
    connection.close()
    return embed


# /info country
async def build_country_embed(self, country_id: int):
    connection = db.pax_engine.connect()
    query = connection.execute(text(
        f'SELECT * FROM players NATURAL JOIN countries NATURAL JOIN religions WHERE country_id = "{country_id}"'
    )).fetchall()
    # Repairing names for multiple players on one country
    names = ''
    for x in query:
        name = await interactions.get(self.bot, interactions.User, object_id=x[2])
        names = f"{name.username}#{name.discriminator} {names}"
    query = list(query[0])
    query[3] = names
    query2 = connection.execute(text(
        f'SELECT SUM(province_pops), COUNT(*) FROM provinces WHERE country_id = "{country_id}"')).fetchone()
    query3 = connection.execute(text(
        f'SELECT province_name FROM provinces WHERE province_id = "{query[10]}"')).fetchone()
    query4 = connection.execute(text(
        f'SELECT COUNT(*) FROM countries WHERE NOT country_id BETWEEN 253 AND 255')).fetchone()
    user = await interactions.get(self.bot, interactions.User, object_id=query[2])
    # Creating embed elements
    embed_footer = interactions.EmbedFooter(
        text=query[13],
        icon_url=query[14]
    )
    embed_thumbnail = interactions.EmbedImageStruct(
        url=query[12]
    )
    embed_author = interactions.EmbedAuthor(
        name=query[3],
        icon_url=user.avatar_url
    )
    f1 = interactions.EmbedField(name="Władca", value=f"```{query[8]}```", inline=True)
    f2 = interactions.EmbedField(name="Ustrój", value=f"```{query[9]}```", inline=True)
    f3 = interactions.EmbedField(name="Stolica", value=f"```ansi\n{query3[0]} \u001b[0;30m({query[10]})```",
                                 inline=True)
    f4 = interactions.EmbedField(name="Domena", value=f"```{query2[1]} prowincji.```", inline=True)
    f5 = interactions.EmbedField(name="Religia", value=f"```{query[16]}```", inline=True)
    f6 = interactions.EmbedField(name="Populacja", value=f"```{query2[0]} osób.```", inline=True)
    f7 = interactions.EmbedField(name="Dyplomacja", value=f"{query[15]}", inline=True)
    f8 = interactions.EmbedField(name="ID Kraju", value=f"{country_id} / {query4[0]}", inline=True)

    # Building the Embed
    embed = interactions.Embed(
        color=int(query[7], 16),
        title=query[5],
        # description=result_countries[5],
        url=query[11],
        footer=embed_footer,
        thumbnail=embed_thumbnail,
        author=embed_author,
        fields=[f1, f2, fb, f3, f4, fb, f5, f6, fb, f7, f8]
    )
    connection.close()
    return embed


# /inventory items
async def build_item_embed_good(ctx, self, item_id: int, country_id: int, item_query: list):
    province_query = db.pax_engine.connect().execute(text(
        f'SELECT item_id, item_name, item_color, item_image_url, item_desc, quantity, item_good '
        f'FROM items NATURAL JOIN inventories '
        f'WHERE item_id = "{item_id}" AND country_id = "{country_id}"'
    )).fetchone()
    # Creating embed elements
    user = await interactions.get(self.bot, interactions.User, object_id=ctx.author.id)
    embed_thumbnail = interactions.EmbedImageStruct(
        url=item_query[3]
    )
    embed_author = interactions.EmbedAuthor(
        name=user.username + "#" + user.discriminator,
        icon_url=user.avatar_url
    )
    f1 = interactions.EmbedField(name="Opis", value=f"```{item_query[4]}```", inline=False)
    f2 = interactions.EmbedField(name="Prowincje ze złożami",
                                 value=f"```ansi"
                                       f"\n\u001b[0;30m#53  \u001b[0;37mTestowa Prowincja\u001b[0;0m"
                                       f"\n\u001b[0;30m#58  \u001b[0;37mKontantinolopolis\u001b[0;0m"
                                       f"\n"
                                       f"\n‎```", inline=True)
    f3 = interactions.EmbedField(name="Ekonomia",
                                 value=f"```ansi"
                                       f"\nZasoby:   \u001b[0;37m       273\u001b[0;0m"
                                       f"\nPrzychód: \u001b[0;32m      +32\u001b[0;0m"
                                       f"\nDeficyt:  \u001b[0;31m      -20\u001b[0;0m"
                                       f"\nBalans:   \u001b[0;33m      +12\u001b[0;0m```",
                                 inline=True)
    f4 = interactions.EmbedField(name="Budynki", value=f"```Test Opsem Lirum Lelum Palelum Sinco Sia```", inline=False)
    # Building the Embed
    embed = interactions.Embed(
        color=int(item_query[2], 16),
        title=f"{item_query[1]} #{item_query[0]}",
        # description=result_countries[5],
        thumbnail=embed_thumbnail,
        author=embed_author,
        fields=[f1, f2, f3, f4]
    )
    return embed


async def build_item_embed_talar(ctx, self):
    user = await interactions.get(self.bot, interactions.User, object_id=ctx.author.id)
    embed_thumbnail = interactions.EmbedImageStruct(
        url="https://i.imgur.com/4MFkrcH.png"
    )
    embed_author = interactions.EmbedAuthor(
        name=user.username + "#" + user.discriminator,
        icon_url=user.avatar_url
    )
    f1 = interactions.EmbedField(name="Co ty tutaj kurwa robisz?",
                                 value=f"```Siedzę cicho, nie rzucam się w oczy i wypełniam swoje zadanie jako "
                                       f"item testowy. Więc jeśli nic więcej nie potrzebujesz, to wypierdalaj.```",
                                 inline=False)
    # Building the Embed
    embed = interactions.Embed(
        color=int("000000", 16),
        title=f"Talar #1",
        thumbnail=embed_thumbnail,
        author=embed_author,
        fields=[f1]
    )
    meme = ("https://i.imgur.com/vv5uOH4.png", "https://i.imgur.com/PI9TTwZ.png", "https://i.imgur.com/KJFCoNA.png"
            "https://i.imgur.com/yV4QfJM.png", "https://i.imgur.com/Rr7Ko4w.png", "https://i.imgur.com/L2DNU9a.png")
    embed.set_image(url=random.choice(meme))
    return embed


async def build_item_embed_talary(ctx, self, item_id: int, country_id: int, item_query: list):
    province_query = db.pax_engine.connect().execute(text(
        f'SELECT item_id, item_name, item_color, item_image_url, item_desc, quantity, item_good '
        f'FROM items NATURAL JOIN inventories '
        f'WHERE item_id = "{item_id}" AND country_id = "{country_id}"'
    )).fetchone()
    user = await interactions.get(self.bot, interactions.User, object_id=ctx.author.id)
    embed_thumbnail = interactions.EmbedImageStruct(
        url=item_query[3]
    )
    embed_author = interactions.EmbedAuthor(
        name=user.username + "#" + user.discriminator,
        icon_url=user.avatar_url
    )
    f1 = interactions.EmbedField(name="Opis", value=f"```{item_query[4]}```", inline=False)
    f2 = interactions.EmbedField(name="Oddziały",
                                 value=f"```ansi"
                                       f"\n\u001b[0;37mArmia:          \u001b[0;0m\u001b[0;31m-973"
                                       f"\n\u001b[0;37mBudynki:        \u001b[0;0m\u001b[0;31m-234"
                                       f"\n\u001b[0;37mManufaktury:    \u001b[0;0m\u001b[0;32m+663"
                                       f"\n\u001b[0;37mPodatki:        \u001b[0;0m\u001b[0;32m+1452"
                                       f"```", inline=True)
    f3 = interactions.EmbedField(name="Ekonomia",
                                 value=f"```ansi"
                                       f"\nZasoby:   \u001b[0;37m       7973\u001b[0;0m"
                                       f"\nPrzychód: \u001b[0;32m      +2115\u001b[0;0m"
                                       f"\nDeficyt:  \u001b[0;31m      -1207\u001b[0;0m"
                                       f"\nBalans:   \u001b[0;33m      +908\u001b[0;0m```",
                                 inline=True)
    # Building the Embed
    embed = interactions.Embed(
        color=int(item_query[2], 16),
        title=f"{item_query[1]} #{item_query[0]}",
        # description=result_countries[5],
        thumbnail=embed_thumbnail,
        author=embed_author,
        fields=[f1, f2, f3]
    )
    return embed


async def build_item_embed(ctx, self, item_id: int, country_id: int):
    print(item_id, country_id)
    # Get all info from database
    item_query = db.pax_engine.connect().execute(text(
        f'SELECT item_id, item_name, item_color, item_image_url, item_desc, quantity, item_good '
        f'FROM items NATURAL JOIN inventories '
        f'WHERE item_id = "{item_id}" AND country_id = "{country_id}"'
    )).fetchone()
    if item_query[5] <= 0:  # Redundant check for quantity
        return
    if item_query[6] == 1:  # Get info for items that are also goods on the map
        embed = await build_item_embed_good(ctx, self, item_id, country_id, item_query)
    else:  # Get info for items that are NOT goods on the map
        match item_query[0]:
            case 1:  # Talar
                embed = await build_item_embed_talar(ctx, self)
            case 2:  # Talary
                embed = await build_item_embed_talary(ctx, self, item_id, country_id, item_query)
            case _:
                embed = await build_item_embed_good(ctx, self, item_id, country_id, item_query)
    print(item_query)
    return embed


async def build_item_embed_admin(item_id: int):
    connection = db.pax_engine.connect()
    query = connection.execute(text(
        f'SELECT * FROM items WHERE item_id = "{item_id}"'
    )).fetchall()
    query = list(query[0])
    # Creating embed elements
    embed_thumbnail = interactions.EmbedImageStruct(
        url=query[4]
    )
    f1 = interactions.EmbedField(name="Opis", value=f"```{query[2]}```", inline=True)

    # Building the Embed
    embed = interactions.Embed(
        color=int(query[5], 16),
        title=query[1],
        # description=result_countries[5],
        thumbnail=embed_thumbnail,
        fields=[f1]
    )
    connection.close()
    return embed


# /commands
author = interactions.EmbedAuthor(name="[] - Wymagane, () - Opcjonalne, {} - Dla adminów",
                                  icon_url="https://i.imgur.com/4MFkrcH.png")
fb = interactions.EmbedField(name="", value="", inline=False)


def commands():
    f1 = interactions.EmbedField(name="Information",
                                 value=f"```ansi"
                                       f"\n\u001b[0;31m/tutorial\u001b[0;0m"
                                       f"\nPoradnik mechanik Pax Zeonica."
                                       f"\n\u001b[0;31m/commands\u001b[0;0m"
                                       f"\nWłaśnie tutaj jesteś!"
                                       f"\n\u001b[0;31m/info command\u001b[0;0m"
                                       f"\nInformacje o komendach."
                                       f"\n\u001b[0;31m/info country\u001b[0;0m"
                                       f"\nInformacje o państwach."
                                       f"\n\u001b[0;31m/map\u001b[0;0m"
                                       f"\nGenerowanie map Zeonici.```", inline=True)
    f2 = interactions.EmbedField(name="Inventory",
                                 value=f"```ansi"
                                       f"\n\u001b[0;32m/inventory list\u001b[0;0m"
                                       f"\nLista itemów w twoim inventory."
                                       f"\n\u001b[0;32m/inventory items\u001b[0;0m"
                                       f"\nSzczegóły o typach itemów w twoim inventory."
                                       f"\n\u001b[0;32m/inventory give\u001b[0;0m"
                                       f"\nTransferowanie itemów między graczami.```", inline=True)
    f3 = interactions.EmbedField(name="Army",
                                 value=f"```ansi"
                                       f"\n\u001b[0;33m/army list\u001b[0;0m"
                                       f"\nLista twoich powołanych armii."
                                       f"\n\u001b[0;33m/army templates\u001b[0;0m"
                                       f"\nLista twoich jednostek."
                                       f"\n\u001b[0;33m/army recruit\u001b[0;0m"
                                       f"\nRekrutowanie armii."
                                       f"\n\u001b[0;33m/army disband\u001b[0;0m"
                                       f"\nRozwiązywanie armii."
                                       f"\n\u001b[0;33m/army reorg\u001b[0;0m"
                                       f"\nReorganizacja armii w prowincji."
                                       f"\n\u001b[0;33m/army reinforce\u001b[0;0m"
                                       f"\nUzupełnienie uszkodzonej jednostki."
                                       f"\n\u001b[0;33m/army rename\u001b[0;0m"
                                       f"\nZmiana nazwy armii lub oddziału."
                                       f"\n\u001b[0;33m/army move\u001b[0;0m"
                                       f"\nRuch jednostki po mapie."
                                       f"\n\u001b[0;33m/army orders\u001b[0;0m"
                                       f"\nLista rozkazów na kolejną turę.```", inline=True)
    f4 = interactions.EmbedField(name="Buildings",
                                 value=f"```ansi"
                                       f"\n\u001b[0;34m/building list\u001b[0;0m"
                                       f"\nLista twoich zbudowanych budynków."
                                       f"\n\u001b[0;34m/building templates\u001b[0;0m"
                                       f"\nLista twoich szablonów budynków."
                                       f"\n\u001b[0;34m/building build\u001b[0;0m"
                                       f"\nBudowanie budynków."
                                       f"\n\u001b[0;34m/building destroy\u001b[0;0m"
                                       f"\nNiszczenie budynków."
                                       f"\n\u001b[0;34m/building upgrade\u001b[0;0m"
                                       f"\nUlepszanie budynków.```", inline=True)
    f5 = interactions.EmbedField(name="Provinces",
                                 value=f"```ansi"
                                       f"\n\u001b[0;36m/province list\u001b[0;0m"
                                       f"\nLista prowincji twojego państwa."
                                       f"\n\u001b[0;36m/province rename\u001b[0;0m"
                                       f"\nZmiana nazwy prowincji.```", inline=True)

    embed = interactions.Embed(
        title="Komendy",
        description="Ściąga wszystkich komend istniejących na serwerze Pax Zeonica.\n"
                    "Jeśli chcesz się dowiedzieć więcej na temat danej komendy, użyj:\n"
                    "`/info command [Nazwa Komendy]`.",
        author=author,
        fields=[f1, f2, fb, f3, f4, fb, f5]
    )
    return embed


# /info command
def ic_tutorial():
    f1 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/tutorial\u001b[0;0m```"
                                       f"\nTalar nie będzie czekał!", inline=False)
    embed = interactions.Embed(
        title="/tutorial",
        description="Wyświetla tutorial do gry Pax Zeonica.\n"
                    "Dla przyjemnej gry zachęcamy zapoznać się z tutejszymi mechanikami i komendami.",
        author=author,
        fields=[f1]
    )
    return embed


def ic_commands():
    f1 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/commands\u001b[0;0m```"
                                       f"\nWyświetla ściągę komend.", inline=False)
    embed = interactions.Embed(
        title="/commands",
        description="Wyświetla ściągę wszystkich komend na serwerze Pax Zeonica.",
        author=author,
        fields=[f1]
    )
    return embed


def ic_info_command():
    f1 = interactions.EmbedField(name="[komenda]", value=f"```ansi"
                                                         f"\n\u001b[0;31m•Nazwa Komendy\u001b[0;0m"
                                                         f"\nWyświetla informacje danej komendy.```", inline=True)
    f2 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/info command [/info command]\u001b[0;0m```"
                                       f"\nWyświetla stronę na której się właśnie znajdujesz.", inline=False)
    embed = interactions.Embed(
        title="/info command [komenda]",
        description="Wyświetla dokładne informacje dotyczące danej komendy.\n"
                    "Właśnie jej używasz żeby sprawdzić informacje o komendzie '/info command'.",
        author=author,
        fields=[f1, f2]
    )
    return embed


def ic_info_country():
    f1 = interactions.EmbedField(name="[kraj]", value=f"```ansi"
                                                      f"\n\u001b[0;31m•@ gracza\u001b[0;0m"
                                                      f"\nWyświetla informacje o kraju danego gracza."
                                                      f"\n\u001b[0;31m•Nazwa Kraju\u001b[0;0m"
                                                      f"\nWyświetla informacje o danym kraju.```", inline=True)
    f2 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/info country [@XnraD]\u001b[0;0m```"
                                       f"\nWyświetla informacje o kraju XnraD'a (Karbadia)."
                                       f"```ansi\n\u001b[0;40m/info country [Karbadia]\u001b[0;0m```"
                                       f"\nWyświetla informacje o kraju Karbadia.", inline=False)
    embed = interactions.Embed(
        title="/info country [kraj]",
        description="Wyświetla informacje dotyczące danego kraju.",
        author=author,
        fields=[f1, f2]
    )
    return embed


def ic_map():
    f1 = interactions.EmbedField(name="[mapa]", value=f"```ansi"
                                                      f"\n\u001b[0;31m•Prowincji\u001b[0;0m"
                                                      f"\n321 kolorowych prowincji."
                                                      f"\n\u001b[0;31m•Regionów\u001b[0;0m"
                                                      f"\n30 regionów zeonici."
                                                      f"\n\u001b[0;31m•Zasobów\u001b[0;0m"
                                                      f"\n29 różnych zasobów."
                                                      f"\n\u001b[0;31m•Polityczna\u001b[0;0m"
                                                      f"\nWasze świetne państwa."
                                                      f"\n\u001b[0;31m•Religii\u001b[0;0m"
                                                      f"\nReligie wasze i nasze."
                                                      f"\n\u001b[0;31m•Populacji\u001b[0;0m"
                                                      f"\nPopulacje prowincji."
                                                      f"\n\u001b[0;31m•Autonomii\u001b[0;0m"
                                                      f"\nAutnomie prowincji."
                                                      f"\n\u001b[0;31m•Pusta\u001b[0;0m"
                                                      f"\nPuste płótno.```", inline=True)
    f2 = interactions.EmbedField(name="[kontury]", value=f"```ansi"
                                                         f"\n\u001b[0;32m•Nie\u001b[0;0m"
                                                         f"\nBez konturów."
                                                         f"\n\u001b[0;32m•Tak\u001b[0;0m"
                                                         f"\nZ konturami.```", inline=True)
    f3 = interactions.EmbedField(name="[adnotacje]", value=f"```ansi"
                                                           f"\n\u001b[0;33m•Żadne\u001b[0;0m"
                                                           f"\nBrak adnotacji."
                                                           f"\n\u001b[0;33m•ID Prowincji\u001b[0;0m"
                                                           f"\nNumery prowincji."
                                                           f"\n\u001b[0;33m•Nazwy Prowincji\u001b[0;0m"
                                                           f"\nNazwy waszych prowincji."
                                                           f"\n\u001b[0;33m•Nazwy Regionów\u001b[0;0m"
                                                           f"\nNazwy regionów Zeonici."
                                                           f"\n\u001b[0;33m•Nazwy Państw\u001b[0;0m"
                                                           f"\nNazwy waszych państw."
                                                           f"\n\u001b[0;33m•Armie\u001b[0;0m"
                                                           f"\nAdnotacje armii.```", inline=True)
    f4 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\u001b[0;35m•admin\u001b[0;0m"
                                                       f"\nPokazuje wszystkie możliwe informacje.```", inline=True)
    f5 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/mapa [Polityczna] [Nie] [Armie]\u001b[0;0m```"
                                       f"\nGeneruje mapę z państwami graczy i armiami."
                                       f"```ansi\n\u001b[0;40m/mapa [Prowincji] [Tak] [ID Prowincji]\u001b[0;0m```"
                                       f"\nGeneruje mapę prowincji, konturami i ID prowincji.", inline=False)

    embed = interactions.Embed(
        title="/map [mapa] [kontury] [adnotacje] {admin}",
        description="Za pomocą tej komendy możesz wygenerować sobie własną mapę Zeonici!\n"
                    "Niektóre mapy mają informacje przeznaczone tylko dla gracza który wysyła komendę, "
                    "więc uważaj na publicznych kanałach!\n"
                    "Czas generowania wacha się od kilku dla najprostszych map do nawet kilkunastu sekund.",
        author=author,
        fields=[f1, f3, fb, f2, f4, f5]
    )
    return embed


def ic_inventory_list():
    f1 = interactions.EmbedField(name="[tryb]", value=f"```ansi"
                                                      f"\n\u001b[0;31m•Dokładny\u001b[0;0m"
                                                      f"\nInformacje w postaci szczegółowych stron."
                                                      f"\n\u001b[0;31m•Prosty\u001b[0;0m"
                                                      f"\nInformacje w postaci prostej listy.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi"
                                                       f"\n\u001b[0;35m•@ gracza\u001b[0;0m"
                                                       f"\nWyświetla inventory kraju danego gracza."
                                                       f"\n\u001b[0;35m•Nazwa Kraju\u001b[0;0m"
                                                       f"\nWyświetla inventory danego kraju.```", inline=True)
    f3 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/inventory list [Dokładny]\u001b[0;0m```"
                                       f"\nWyświela ekwipunek w postaci stron."
                                       f"```ansi\n\u001b[0;40m/inventory list [Prosty]\u001b[0;0m```"
                                       f"\nWyświela ekwipunek w postaci listy.", inline=False)
    embed = interactions.Embed(
        title="/inventory list [tryb] {admin}",
        description="Wyświetla ilość itemów które posiada państwo gracza oraz ich balans.\n"
                    "W trybie dokładnym wyświetla również więcej informacji, np. szczegóły wydatków.",
        author=author,
        fields=[f1, f2, f3]
    )
    return embed


def ic_inventory_item():
    f1 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/inventory item\u001b[0;0m```"
                                       f"\nWyświetla informacje o itemach.", inline=False)
    embed = interactions.Embed(
        title="/inventory item",
        description="Wyświetla informacje o itemach które posiada państwo gracza.",
        author=author,
        fields=[f1]
    )
    return embed


def ic_inventory_give():
    f1 = interactions.EmbedField(name="[kraj]", value=f"```ansi"
                                                      f"\n\u001b[0;31m•@ gracza\u001b[0;0m"
                                                      f"\nGracz do którego kraju chcemy dać itemy."
                                                      f"\n\u001b[0;31m•Nazwa Kraju\u001b[0;0m"
                                                      f"\nKraj do którego chcemy dać itemy.```", inline=True)
    f2 = interactions.EmbedField(name="[argument]", value=f"```ansi"
                                                          f"\n\u001b[0;32m•Item | ilość\u001b[0;0m"
                                                          f"\nRodzaj i ilość itemów które chcemy dać.```", inline=True)
    f3 = interactions.EmbedField(name="{admin}", value=f"```ansi"
                                                       f"\n\u001b[0;35m•admin\u001b[0;0m"
                                                       f"\nPozwala na spawnowanie itemów.```", inline=True)
    f4 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/inventory give [@XnraD] [10 Talary]\u001b[0;0m```"
                                       f"\nDaje państwu XnraD'a (Karbadia) 10 talarów."
                                       f"```ansi\n\u001b[0;40m/inventory give [Karbadia] [15 Drewno,"
                                       f" 20 Kamień]\u001b[0;0m```"
                                       f"\nDaje państwu Karbadia 15 drewna i 20 kamienia.", inline=False)
    embed = interactions.Embed(
        title="/inventory give [kraj] [argument] {admin}",
        description="Daje innemu krajowi itemy z twojego inventory.\n"
                    "Uważaj z kim handlujesz - jeśli ktoś nie dotrzyma umowy, to twój problem IC!",
        author=author,
        fields=[f1, f2, f3, f4]
    )
    return embed


def ic_army_list():
    f1 = interactions.EmbedField(name="[tryb]", value=f"```ansi"
                                                      f"\n\u001b[0;31m•Dokładny\u001b[0;0m"
                                                      f"\nInformacje w postaci szczegółowych stron."
                                                      f"\n\u001b[0;31m•Prosty\u001b[0;0m"
                                                      f"\nInformacje w postaci prostej listy.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\n\u001b[0;35m•admin\u001b[0;0m"
                                                       f"\nWyświetla wszystkie armie."
                                                       f"\n\u001b[0;35m•@ gracza\u001b[0;0m"
                                                       f"\nWyświetla armie kraju danego gracza."
                                                       f"\n\u001b[0;35m•Nazwa Kraju\u001b[0;0m"
                                                       f"\nWyświetla armie danego kraju.```", inline=True)
    f3 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/army list [Dokładny]\u001b[0;0m```"
                                       f"\nWyświela armie w postaci stron."
                                       f"```ansi\n\u001b[0;40m/army list [Prosty]\u001b[0;0m```"
                                       f"\nWyświela armie w postaci listy.", inline=False)
    embed = interactions.Embed(
        title="/army list [tryb] {admin}",
        description="Wyświetla powołane armie które posiada państwo gracza.\n"
                    "W trybie dokładnym wyświetla również więcej informacji, np. pochodzenie jednostki.",
        author=author,
        fields=[f1, f2, f3]
    )
    return embed


def ic_army_templates():
    f1 = interactions.EmbedField(name="[jednostka]", value=f"```ansi"
                                                           f"\n\u001b[0;31m•Szablon jednostki\u001b[0;0m"
                                                           f"\nWyświetla szablon danej jednostki.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\n\u001b[0;35m•admin\u001b[0;0m"
                                                       f"\nWyświetla wszystkie szablony jednostek."
                                                       f"\n\u001b[0;35m•@ gracza\u001b[0;0m"
                                                       f"\nWyświetla szablony jednostek kraju danego gracza."
                                                       f"\n\u001b[0;35m•Nazwa Kraju\u001b[0;0m"
                                                       f"\nWyświetla szablony jednostek danego kraju.```", inline=True)
    f3 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/army template [Wojownicy]\u001b[0;0m```"
                                       f"\nWyświela informacje o szablonie jednostki 'Wojownicy'.", inline=False)
    embed = interactions.Embed(
        title="/army template [jednostka] {admin}",
        description="Wyświetla informacje o szablonach jednostek państwa gracza.",
        author=author,
        fields=[f1, f2, f3]
    )
    return embed


def ic_army_recruit():
    f1 = interactions.EmbedField(name="[prowincja]", value=f"```ansi"
                                                           f"\n\u001b[0;31m•# prowincji\u001b[0;0m"
                                                           f"\nZ prowincji o tym ID będzie pochodzić jednostka."
                                                           f"\n\u001b[0;31m•Nazwa prowincji\u001b[0;0m"
                                                           f"\nZ prowincji o ten nazwie będzie pochodzić jednostka.```",
                                 inline=True)
    f2 = interactions.EmbedField(name="[jednostka]", value=f"```ansi"
                                                           f"\n\u001b[0;32m•Szablon jednostki\u001b[0;0m"
                                                           f"\nTaka jednostka zostanie zrekrutowana.```", inline=True)
    f3 = interactions.EmbedField(name="(nazwa_jednostki)", value=f"```ansi"
                                                                 f"\n\u001b[0;33m•Nazwa Jednostki\u001b[0;0m"
                                                                 f"\nNazwa nowo utworzonej jednostki.```", inline=True)
    f4 = interactions.EmbedField(name="(nazwa_armii)", value=f"```ansi"
                                                             f"\n\u001b[0;34m•Nazwa Armii\u001b[0;0m"
                                                             f"\nNazwa nowo utworzonej armii.```", inline=True)
    f5 = interactions.EmbedField(name="{admin}", value=f"```ansi"
                                                       f"\n\u001b[0;35m•@ gracza\u001b[0;0m"
                                                       f"\nSpawnuje jednostkę krajowi danego gracza."
                                                       f"\n\u001b[0;35m•Nazwa Kraju\u001b[0;0m"
                                                       f"\nSpawnuje jednostkę danemu krajowi.```", inline=True)
    f6 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/army recruit [53] [Wojownicy]\u001b[0;0m```"
                                       f"\nRekrutuje w prowincji #53 jednostkę Wojowników i nadaje im automatycznie"
                                       f"wygenerowaną nazwę jednostki oraz armii."
                                       f"\nOdejmuje potrzebną ilość populacji z prowincji #53."
                                       f"\nOdejmuje potrzebną ilość pozostałych itemów z inventory."
                                       f"```ansi\n\u001b[0;40m/army recruit [53] [Wojownicy] (Gwardia Królewska) "
                                       f"(Pierwsza Chorągiew)\u001b[0;0m```"
                                       f"\nTo samo co wyżej, ale na dodatek ustawia nazwę jednostki oraz nazwę armii co"
                                       f" ułatwia jej przyszłe zarządzanie i dodaje nam rigczu na polu bitwy.",
                                 inline=False)
    embed = interactions.Embed(
        title="/army recruit [prowincja] [jednostka] (nazwa_jednostki) (nazwa_armii) {admin}",
        description="Rekrutuje daną jednostkę w danej prowincji.\n"
                    "Pobiera potrzebną ilość populacji z rekrutowanej prowincji oraz surowce z ekwipunku.\n"
                    "Nazwy jednostek ani armii nie mogą się duplikować.",
        author=author,
        fields=[f1, f5, fb, f2, f3, f4, f6]
    )
    return embed


def ic_army_disband():
    f1 = interactions.EmbedField(name="[typ]", value=f"```ansi"
                                                     f"\n\u001b[0;31m•Armia\u001b[0;0m"
                                                     f"\nRozwiązuje armię."
                                                     f"\n\u001b[0;31m•Jednotska\u001b[0;0m"
                                                     f"\nRozwiązuje jednostkę.```",
                                 inline=True)
    f2 = interactions.EmbedField(name="[nazwa]", value=f"```ansi"
                                                       f"\n\u001b[0;32m•# jednostki lub armii\u001b[0;0m"
                                                       f"\nRozwiązuje jednostkę lub armię o danym ID."
                                                       f"\n\u001b[0;32m•Nazwa jednostki lub armii\u001b[0;0m"
                                                       f"\nRozwiązuje jednostkę lub armię o danej nazwie.```",
                                 inline=True)
    f3 = interactions.EmbedField(name="{admin}", value=f"```ansi"
                                                       f"\n\u001b[0;35m•@ gracza\u001b[0;0m"
                                                       f"\nUsuwa jednostkę lub armię krajowi danego gracza."
                                                       f"\n\u001b[0;35m•Nazwa Kraju\u001b[0;0m"
                                                       f"\nUsuwa jednostkę lub armię danemu krajowi.```", inline=True)
    f4 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/army disband [Armia] [Pierwsza Chorągiew]\u001b[0;0m```"
                                       f"\nRozwiązuje całą armię."
                                       f"\nZwraca część kosztów rekrutacyjnych oraz żywych żołnierzy do "
                                       f"prowincji ich pochodzenia."
                                       f"```ansi\n\u001b[0;40m/army disband [Jednostka] [12, 13]\u001b[0;0m```"
                                       f"\nTo samo co wyżej, ale kilka jednostek na raz i po ID.",
                                 inline=False)
    embed = interactions.Embed(
        title="/army disband [typ] [nazwa] {admin}",
        description="Rozwiązuje daną jednostkę zwracając część surowców i odsyłając wojów do domu.\n"
                    "Populacja pobrana podczas rekrutacji wraca do swojej prowincji.\n"
                    "Możesz rozwiązać armie tylko w granicach swojego państwa.",
        author=author,
        fields=[f1, f2, fb, f3, f4]
    )
    return embed


def ic_army_reorg():
    f1 = interactions.EmbedField(name="[prowincja]", value=f"```ansi"
                                                           f"\n\u001b[0;31m•# prowincji\u001b[0;0m"
                                                           f"\nW prowincji o tym ID będzie reorganizacja."
                                                           f"\n\u001b[0;31m•Nazwa prowincji\u001b[0;0m"
                                                           f"\nW prowincji o tej nazwie będzie reorganizacja.```",
                                 inline=True)
    f2 = interactions.EmbedField(name="(argument)", value=f"```ansi"
                                                          "\n\u001b[0;32m•{# armii: # jednostki}\u001b[0;0m"
                                                          f"\nW prowincji o tym ID będzie reorganizacja."
                                                          "\n\u001b[0;32m•{Nazwa armii: Nazwa jednostki}\u001b[0;0m"
                                                          f"\nW prowincji o tej nazwie będzie reorganizacja.```",
                                 inline=True)
    f3 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\n\u001b[0;35m•@ gracza\u001b[0;0m"
                                                       f"\nReorganizuje armię krajowi danego gracza."
                                                       f"\n\u001b[0;35m•Nazwa Kraju\u001b[0;0m"
                                                       f"\nReorganizuje armię danemu krajowi.```", inline=True)
    f4 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/army reorg [53]\u001b[0;0m```"
                                       f"\nWyświela informacje o organizacji armii w prowincji #53."
                                       "```ansi\n\u001b[0;40m/army reorg [53] ({1: +13, +12})\u001b[0;0m```"
                                       f"\nPrzenosi jednostki o #13 i #12 do armii #1."
                                       "```ansi\n\u001b[0;40m/army reorg [53] ({+: +13, +12})\u001b[0;0m```"
                                       f"\nTworzy nową armię o kolejnym wolnym ID i dodaje do niej jednostki #13 i #12."
                                       "```ansi\n\u001b[0;40m/army reorg [53] ({1: -13}, {3; +12})\u001b[0;0m```"
                                       f"\nUsuwa jednostkę #13 z armii #1 i tworzy dla niej nową armię o kolejnym "
                                       f"wolnym ID. Równocześnie dodaje jednostkę #12 do armii #3.",
                                 inline=False)
    embed = interactions.Embed(
        title="/army reorg [prowincja] (argument) {admin}",
        description="Reorganizuje strukturę armii w danej prowincji.\n"
                    "Armie składają się z jednostek, warto połączyć kilka armii w jedną dużą żeby łatwiej móc potem "
                    "nimi zarządzać.",
        author=author,
        fields=[f1, f2, f3, f4]
    )
    return embed


def ic_army_reinforce():
    f1 = interactions.EmbedField(name="[typ]", value=f"```ansi"
                                                     f"\n\u001b[0;31m•Armia\u001b[0;0m"
                                                     f"\nUzupełnia armię."
                                                     f"\n\u001b[0;31m•Jednotska\u001b[0;0m"
                                                     f"\nUzupełnia jednostkę.```", inline=True)

    f2 = interactions.EmbedField(name="[nazwa]", value=f"```ansi"
                                                       f"\n\u001b[0;32m•# jednostki lub armii\u001b[0;0m"
                                                       f"\nUzupełnia jednostkę lub armię o danym ID."
                                                       f"\n\u001b[0;32m•Nazwa jednostki lub armii\u001b[0;0m"
                                                       f"\nUzupełnia jednostkę lub armię o danej nazwie.```",
                                 inline=True)
    f3 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\n\u001b[0;35m•@ gracza | ilość\u001b[0;0m"
                                                       f"\nUzupełnia jednostkę lub armię krajowi danego gracza."
                                                       f"\n\u001b[0;35m•Nazwa Kraju | ilość\u001b[0;0m"
                                                       f"\nUzupełnia jednostkę lub armię danemu krajowi.```",
                                 inline=False)
    f4 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/army resupply [Jednostka] [Gwardia Królewska]"
                                       f"[Gwardia Królewska]\u001b[0;0m```"
                                       f"\nPrzywraca jednostkę 'Gwardia Królewska' do pełni sił."
                                       f"\nGdyby przedtem miała tylko 75% stanu osobowego z powodu bitew lub innych "
                                       f"powodów, teraz wróciła by do 100% sił."
                                       f"\nOdejęte zostanie również 25% bazowego kosztu jednostki z inventory kraju."
                                       f"```ansi\n\u001b[0;40m/army resupply [Armia] [1, 2]\u001b[0;0m```"
                                       f"\nTo samo co wyżej, ale kilka armii na raz.",
                                 inline=False)
    embed = interactions.Embed(
        title="/army reinforce [typ] [jednostka] {admin}",
        description="Uzupełnia uszkodzoną jednostkę do pełni sił.\n"
                    "Pobiera odpowiednią ilość surowców zależną od stopnia uszkodzenia i bazowego kosztu jednostki.",
        author=author,
        fields=[f1, f2, f3, f4]
    )
    return embed


def ic_army_rename():
    f1 = interactions.EmbedField(name="[typ]", value=f"```ansi"
                                                     f"\n\u001b[0;31m•Armia\u001b[0;0m"
                                                     f"\nZmienia nazwę armii."
                                                     f"\n\u001b[0;31m•Jednotska\u001b[0;0m"
                                                     f"\nZmienia nazwę jednostki.```", inline=True)
    f2 = interactions.EmbedField(name="[nazwa]", value=f"```ansi"
                                                       f"\n\u001b[0;32m•# jednostki lub armii\u001b[0;0m"
                                                       f"\nZmienia nazwę jednostce lub armii o danym ID."
                                                       f"\n\u001b[0;32m•Nazwa jednostki lub armii\u001b[0;0m"
                                                       f"\nZmienia nazwę jednostce lub armii o danej nazwie.```",
                                 inline=True)
    f3 = interactions.EmbedField(name="[nowa_nazwa]", value=f"```ansi"
                                                            f"\n\u001b[0;33m•Nowa nazwa\u001b[0;0m"
                                                            f"\nNadaje nową nazwę jednostce lub armii.```",
                                 inline=True)
    f4 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\n\u001b[0;35m•@ gracza\u001b[0;0m"
                                                       f"\nZmienia nazwę jednostki lub armii krajowi danego gracza."
                                                       f"\n\u001b[0;35m•Nazwa Kraju\u001b[0;0m"
                                                       f"\nZmienia nazwę jednostki lub armii danemu krajowi.```",
                                 inline=True)
    f5 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/army rename [Armia] [Pierwsza Chorągiew] "
                                       f"[Chorągiew Cara] \u001b[0;0m```"
                                       f"\nZmienia nazwę armii 'Pierwsza Chorągiew' na 'Chorągiew Cara'."
                                       f"```ansi\n\u001b[0;40m/army rename [Jednostka] [13] "
                                       f"[Gwardia Cara] \u001b[0;0m```"
                                       f"\nZmienia nazwę jednostki #13 na 'Gwardia Cara'.",
                                 inline=False)
    embed = interactions.Embed(
        title="/army rename [typ] [nazwa] [nowa_nazwa] {admin}",
        description="Zmienia nazwę jednostki lub armii państwa.\n"
                    "Pozwala na łatwiejsze zarządzanie armią.",
        author=author,
        fields=[f1, f2, fb, f3, f4, f5]
    )
    return embed


def ic_army_move():
    f1 = interactions.EmbedField(name="[mapa]", value=f"```ansi"
                                                      f"\n\u001b[0;31mPusta\u001b[0;0m"
                                                      f"\nPuste płótno.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\u001b[0;35@ gracza lub nazwa kraju\u001b[0;0m"
                                                       f"\nPokazuje inventory danego kraju.```", inline=True)
    embed = interactions.Embed(
        title="/army move Dummy",
        description="Army List",
        author=author,
        fields=[f1]
    )
    return embed


def ic_army_orders():
    f1 = interactions.EmbedField(name="[mapa]", value=f"```ansi"
                                                      f"\n\u001b[0;31mPusta\u001b[0;0m"
                                                      f"\nPuste płótno.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\u001b[0;35@ gracza lub nazwa kraju\u001b[0;0m"
                                                       f"\nPokazuje inventory danego kraju.```", inline=True)
    embed = interactions.Embed(
        title="/army orders Dummy",
        description="Army List",
        author=author,
        fields=[f1]
    )
    return embed


def ic_building_list():
    f1 = interactions.EmbedField(name="[tryb]", value=f"```ansi"
                                                      f"\n\u001b[0;31m•Dokładny\u001b[0;0m"
                                                      f"\nInformacje w postaci szczegółowych stron."
                                                      f"\n\u001b[0;31m•Prosty\u001b[0;0m"
                                                      f"\nInformacje w postaci prostej listy.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\n\u001b[0;35m•admin\u001b[0;0m"
                                                       f"\nWyświetla wszystkie budynki."
                                                       f"\n\u001b[0;35m•@ gracza\u001b[0;0m"
                                                       f"\nWyświetla budynki kraju danego gracza."
                                                       f"\n\u001b[0;35m•Nazwa Kraju\u001b[0;0m"
                                                       f"\nWyświetla budynki danego kraju.```", inline=True)
    f3 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/building list [Dokładny]\u001b[0;0m```"
                                       f"\nWyświela budynki w postaci stron."
                                       f"```ansi\n\u001b[0;40m/army list [Prosty]\u001b[0;0m```"
                                       f"\nWyświela budynki w postaci listy.", inline=False)
    embed = interactions.Embed(
        title="/building list [tryb] {admin}",
        description="Wyświetla zbudowane budynki które posiada państwo gracza.\n"
                    "W trybie dokładnym wyświetla również więcej informacji, np. opisy budynków.",
        author=author,
        fields=[f1, f2, f3]
    )
    return embed


def ic_building_templates():
    f1 = interactions.EmbedField(name="[budynek]", value=f"```ansi"
                                                         f"\n\u001b[0;31m•Szablon budynku\u001b[0;0m"
                                                         f"\nWyświetla szablon danego budynku.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\n\u001b[0;35m•admin\u001b[0;0m"
                                                       f"\nWyświetla wszystkie szablony budynków."
                                                       f"\n\u001b[0;35m•@ gracza\u001b[0;0m"
                                                       f"\nWyświetla szablony budynków kraju danego gracza."
                                                       f"\n\u001b[0;35m•Nazwa Kraju\u001b[0;0m"
                                                       f"\nWyświetla szablony budynków danego kraju.```", inline=True)
    f3 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/building template [Tartak]\u001b[0;0m```"
                                       f"\nWyświela informacje o szablonie budynku 'Tartak'.", inline=False)
    embed = interactions.Embed(
        title="/army template [budynek] {admin}",
        description="Wyświetla informacje o szablonach budynków państwa gracza.",
        author=author,
        fields=[f1, f2, f3]
    )
    return embed


def ic_building_build():
    f1 = interactions.EmbedField(name="[prowincja]", value=f"```ansi"
                                                           f"\n\u001b[0;31m•# prowincji\u001b[0;0m"
                                                           f"\nW prowincji o tym ID będzie wybudowany budynek."
                                                           f"\n\u001b[0;31m•Nazwa prowincji\u001b[0;0m"
                                                           f"\nW prowincji o tej nazwie będzie wybudowany budynek.```",
                                 inline=True)
    f2 = interactions.EmbedField(name="[budynek]", value=f"```ansi"
                                                         f"\n\u001b[0;32m•Szablon budynku\u001b[0;0m"
                                                         f"\nTaki budynek zostanie wybudowany.```", inline=False)
    f3 = interactions.EmbedField(name="{admin}", value=f"```ansi"
                                                       f"\n\u001b[0;35m•@ gracza\u001b[0;0m"
                                                       f"\nSpawnuje budynek krajowi danego gracza."
                                                       f"\n\u001b[0;35m•Nazwa Kraju\u001b[0;0m"
                                                       f"\nSpawnuje budynek danemu krajowi.```", inline=True)
    f4 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/building building [53] [Tartak]\u001b[0;0m```"
                                       f"\nBuduje w prowincji #53 Tartak."
                                       f"\nW prowincji #53 zaczyna pracować dana ilość populacji."
                                       f"\nOdejmuje potrzebną ilość pozostałych itemów z inventory.",
                                 inline=False)
    embed = interactions.Embed(
        title="/building build [prowincja] [budynek] {admin}",
        description="Buduje dany budynek w danej prowincji.\n"
                    "Pobiera potrzebną ilość populacji z rekrutowanej prowincji oraz surowce z inventory.\n",
        author=author,
        fields=[f1, f3, f2, f4]
    )
    return embed


def ic_building_destroy():
    f1 = interactions.EmbedField(name="[budynek]", value=f"```ansi"
                                                         f"\n\u001b[0;31m•# budynku\u001b[0;0m"
                                                         f"\nNiszczy budynek o danym ID.```",
                                 inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi"
                                                       f"\n\u001b[0;35m•@ gracza\u001b[0;0m"
                                                       f"\nUsuwa budynek krajowi danego gracza."
                                                       f"\n\u001b[0;35m•Nazwa Kraju\u001b[0;0m"
                                                       f"\nUsuwa budynek danemu krajowi.```", inline=True)
    f3 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/building destroy [27]\u001b[0;0m```"
                                       f"\nNiszczy budynek #27."
                                       f"\nZwraca część kosztów oraz zwalnia robotników."
                                       f"```ansi\n\u001b[0;40m/army disband [27, 37]\u001b[0;0m```"
                                       f"\nTo samo co wyżej, ale kilka budynków na raz.",
                                 inline=False)
    embed = interactions.Embed(
        title="/building destroy [budynek] {admin}",
        description="Niszczy dany budynek zwracając część surowców do inventory oraz zwalniając robotników.\n"
                    "Możesz zniszczyć tylko budynki które posiadasz oraz kontrolujesz.",
        author=author,
        fields=[f1, f2, f3]
    )
    return embed


def ic_building_upgrade():
    f1 = interactions.EmbedField(name="[budynek]", value=f"```ansi"
                                                         f"\n\u001b[0;31m•# budynku\u001b[0;0m"
                                                         f"\nUlepsza budynek o danym ID.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\n\u001b[0;35m•@ gracza\u001b[0;0m"
                                                       f"\nUlepsza budynek krajowi danego gracza."
                                                       f"\n\u001b[0;35m•Nazwa Kraju\u001b[0;0m"
                                                       f"\nUlepsza budynek danemu krajowi.```", inline=True)
    f3 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/building destroy [27]\u001b[0;0m```"
                                       f"\nNiszczy budynek #27."
                                       f"\nZwraca część kosztów oraz zwalnia robotników."
                                       f"```ansi\n\u001b[0;40m/army disband [27, 37]\u001b[0;0m```"
                                       f"\nTo samo co wyżej, ale kilka budynków na raz.",
                                 inline=False)
    embed = interactions.Embed(
        title="/building upgrade [budynek] {admin}",
        description="Ulepsza dany budynek o jeden poziom.\n"
                    "Nie da się downgrade'ować, jeśli nie chcesz budynku ulepszonego musisz go zniszczyć.",
        author=author,
        fields=[f1, f2, f3]
    )
    return embed


def ic_province_list():
    f1 = interactions.EmbedField(name="[tryb]", value=f"```ansi"
                                                      f"\n\u001b[0;31m•Dokładny\u001b[0;0m"
                                                      f"\nInformacje w postaci szczegółowych stron."
                                                      f"\n\u001b[0;31m•Prosty\u001b[0;0m"
                                                      f"\nInformacje w postaci prostej listy.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi"
                                                       f"\n\u001b[0;35m•@ gracza\u001b[0;0m"
                                                       f"\nWyświetla prowincje kraju danego gracza."
                                                       f"\n\u001b[0;35m•Nazwa Kraju\u001b[0;0m"
                                                       f"\nWyświetla prowincje danego kraju.```", inline=True)
    f3 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/province list [Dokładny]\u001b[0;0m```"
                                       f"\nWyświela prowincje w postaci stron."
                                       f"```ansi\n\u001b[0;40m/province list [Prosty]\u001b[0;0m```"
                                       f"\nWyświela prowincje w postaci listy.", inline=False)
    embed = interactions.Embed(
        title="/province list [tryb] {admin}",
        description="Wyświetla prowincje które posiada kraj.\n"
                    "W trybie dokładnym wyświetla również więcej informacji, np. tamtejsze budynki i armie.",
        author=author,
        fields=[f1, f2, f3]
    )
    return embed


def ic_province_rename():
    f1 = interactions.EmbedField(name="[prowincja]", value=f"```ansi"
                                                           f"\n\u001b[0;32m•# prowincji\u001b[0;0m"
                                                           f"\nZmienia nazwę prowincji o danym ID."
                                                           f"\n\u001b[0;32m•Nazwa prowincji\u001b[0;0m"
                                                           f"\nZmienia nazwę prowincji o danej nazwie.```",
                                 inline=True)
    f2 = interactions.EmbedField(name="[nowa_nazwa]", value=f"```ansi"
                                                            f"\n\u001b[0;33m•Nowa nazwa\u001b[0;0m"
                                                            f"\nNadaje nową nazwę prowincji.```",
                                 inline=True)
    f3 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\n\u001b[0;35m•@ gracza\u001b[0;0m"
                                                       f"\nZmienia nazwę prowincji krajowi danego gracza."
                                                       f"\n\u001b[0;35m•Nazwa Kraju\u001b[0;0m"
                                                       f"\nZmienia nazwę prowincji danemu krajowi.```",
                                 inline=True)
    f4 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/province rename [Kanonia] [Skalla] \u001b[0;0m```"
                                       f"\nZmienia nazwę prowincji 'Kanonia' na 'Skalla'."
                                       f"```ansi\n\u001b[0;40m/province rename [53] [Skalla] \u001b[0;0m```"
                                       f"\nZmienia nazwę prowincji #53 na 'Skalla'.",
                                 inline=False)
    embed = interactions.Embed(
        title="/province rename [nazwa] [nowa_nazwa] {admin}",
        description="Zmienia nazwę prowincji którą gracz posiada i kontroluje.\n"
                    "Pozwala na łatwiejsze zarządzanie prowincjami.",
        author=author,
        fields=[f1, f2, fb, f3, f4]
    )
    return embed
