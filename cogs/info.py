import interactions
from database import *
from sqlalchemy import text
import time


def setup(bot):
    Info(bot)


async def build_refuse_embed(self):
    embed_author = interactions.EmbedAuthor(
        name="Talar",
        icon_url="https://i.imgur.com/kpZr5oC.png"
    )
    f1 = interactions.EmbedField(
        name="Wygeneruj sobie własne!",
        value="... połkie haczyk, spławik - i jeszcze kawałek wędki upierdoli!",
        inline=True
    )
    # Building the Embed
    embed = interactions.Embed(
        title="Łapy precz!",
        # description=result_countries[5],
        color=int("5C4033", 16),
        author=embed_author,
        fields=[f1]
    )
    return embed


async def build_country_embed(self, country_id: str):
    connection = db.pax_engine.connect()
    query = connection.execute(text(
        f'SELECT * FROM players NATURAL JOIN countries NATURAL JOIN religions WHERE country_id = "{country_id}"'
    )).fetchall()
    # Repairing names for multiple players on one country
    names = ''
    for x in query:
        names = f"{x[3]} {names}"
    query = list(query[0])
    query[3] = names
    print(query)
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
    fb = interactions.EmbedField(name="", value="", inline=False)
    f1 = interactions.EmbedField(name="Władca", value=query[8], inline=True)
    f2 = interactions.EmbedField(name="Ustrój", value=query[9], inline=True)
    f3 = interactions.EmbedField(name="Stolica", value=f"{query3[0]} ({query[10]})", inline=True)
    f4 = interactions.EmbedField(name="Domena", value=f"{query2[1]} prowincji.", inline=True)
    f5 = interactions.EmbedField(name="Religia", value=query[15], inline=True)
    f6 = interactions.EmbedField(name="Populacja", value=f"{query2[0]} osób.", inline=True)
    # f7 = interactions.EmbedField(name="Autonomia", value=autonomy, inline=True)
    f8 = interactions.EmbedField(name="Dyplomacja", value="<#1084509996106137632>", inline=True)
    f9 = interactions.EmbedField(name="Wydarzenia", value="<#1064216866798710904>", inline=True)
    f10 = interactions.EmbedField(name="ID Kraju", value=f"{country_id} / {query4[0]}", inline=True)

    # Building the Embed
    embed = interactions.Embed(
        color=int(query[7], 16),
        title=query[5],
        # description=result_countries[5],
        url=query[11],
        footer=embed_footer,
        thumbnail=embed_thumbnail,
        author=embed_author,
        fields=[f1, f2, fb, f3, f4, fb, f5, f6, fb, f8, f9, f10]
    )
    connection.close()
    return embed


async def build_select_menu():
    connection = db.pax_engine.connect()
    options = []
    query = connection.execute(text(
        f'SELECT country_name, country_id, country_desc FROM countries WHERE country_id NOT BETWEEN 253 AND 255')).fetchall()

    for row in query:
        options.append(interactions.SelectOption(label=f"{row[0]}", value=f"{row[1]}", description=f"{row[2]}"))
    return options


class Info(interactions.Extension):

    def __init__(self, bot):
        self.bot = bot

    @interactions.extension_command(description='Testuj', scope='917078941213261914')  # , scope='917078941213261914'
    async def info(self, ctx: interactions.CommandContext):
        pass

    @info.subcommand(description="Informacje o komendach.")
    @interactions.option(description='The test', required=True,
                         choices=[interactions.Choice(name="/mapa", value="map"),
                                  interactions.Choice(name="/armia", value="army")]
                         )
    async def komenda(self, ctx: interactions.CommandContext, command_name: str):
        match command_name:
            case "map":
                embed_footer = interactions.EmbedFooter(
                    text="test footer",
                    icon_url="https://i.imgur.com/fKL31aD.jpg"
                )
                embed_thumbnail = interactions.EmbedImageStruct(
                    url="https://i.imgur.com/TwROy0B.png",
                    height=50,
                    width=50
                )
                embed = interactions.Embed(
                    color=0xe8d44f,
                    title="/mapa",
                    description="Mapa to komenda.",
                    url="https://imgur.com/C5MGo6o",
                    footer=embed_footer,
                    thumbnail=embed_thumbnail
                )
            case "army":
                embed_footer = interactions.EmbedFooter(
                    text="test footer",
                    icon_url="https://i.imgur.com/fKL31aD.jpg"
                )
                embed_thumbnail = interactions.EmbedImageStruct(
                    url="https://i.imgur.com/TwROy0B.png",
                    height=50,
                    width=50
                )
                embed = interactions.Embed(
                    color=0xe8d44f,
                    title="/mapa",
                    description="Mapa to komenda.",
                    url="https://imgur.com/C5MGo6o",
                    footer=embed_footer,
                    thumbnail=embed_thumbnail
                )
        await ctx.send(embeds=embed)

    @info.subcommand(description="Informacje o krajach.")
    @interactions.option(description='Wpisz dokładną nazwę kraju lub zpinguj gracza.', required=True)
    async def kraj(self, ctx: interactions.CommandContext, c_input: str):

        st = time.time()
        connection = db.pax_engine.connect()
        if c_input.startswith('<@') and c_input.endswith('>'):  # if a ping
            # id = c_input[2:-1]
            country_id = connection.execute(text(
                f'SELECT country_id FROM players NATURAL JOIN countries WHERE player_id = {c_input[2:-1]}')).fetchone()
            if country_id is None:
                await ctx.send('Ten gracz nie ma przypisanego państwa.')
                connection.close()
                return
        else:  # If string is (hopefully) a country name.
            country_id = connection.execute(
                text(f'SELECT country_id FROM players NATURAL JOIN countries WHERE country_name = "{c_input}"'
                     )).fetchone()
            if country_id is None:
                await ctx.send('Takie państwo nie istnieje.')
                connection.close()
                return
        options = await build_select_menu()

        selection = interactions.SelectMenu(
            options=options,
            placeholder="Kraje",
            custom_id="countries_select",
            )
        print(country_id, country_id[0])
        print(ctx.author.id)
        embeds = await build_country_embed(self, country_id[0])
        et = time.time()
        print(et-st)

        await ctx.send(embeds=embeds, components=selection)

    @interactions.extension_component("countries_select")
    async def on_select(self, ctx: interactions.ComponentContext, options: list[str]):
        print(ctx.author.id)
        print(ctx.message.interaction.user.id)
        if ctx.author.id == ctx.message.interaction.user.id:
            embeds = await build_country_embed(self, options[0])
            await ctx.edit(embeds=embeds)
            await ctx.disable_all_components()
        else:
            embeds = await build_refuse_embed(self)
            await ctx.send(embeds=embeds, ephemeral=True)

