import interactions
from database import *
from sqlalchemy import text
import time
from interactions.ext.paginator import Page, Paginator


def setup(bot):
    Info(bot)


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
    f1 = interactions.EmbedField(name="Władca", value=f"```{query[8]}```", inline=True)
    f2 = interactions.EmbedField(name="Ustrój", value=f"```{query[9]}```", inline=True)
    f3 = interactions.EmbedField(name="Stolica", value=f"```ansi\n{query3[0]} \u001b[0;30m({query[10]})```",
                                 inline=True)
    f4 = interactions.EmbedField(name="Domena", value=f"```{query2[1]} prowincji.```", inline=True)
    f5 = interactions.EmbedField(name="Religia", value=f"```{query[15]}```", inline=True)
    f6 = interactions.EmbedField(name="Populacja", value=f"```{query2[0]} osób.```", inline=True)
    f7 = interactions.EmbedField(name="Dyplomacja", value="<#1084509996106137632>", inline=True)
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
                await ctx.send(f'Państwo - {c_input} - nie istnieje.')
                connection.close()
                return
        else:  # If string is (hopefully) a country name.
            country_id = None
            if '"' in c_input:
                pass
            else:
                country_id = connection.execute(
                    text(f'SELECT country_id FROM players NATURAL JOIN countries WHERE country_name = "{c_input}"'
                         )).fetchone()
            if country_id is None:
                await ctx.send(f'Państwo - {c_input} - nie istnieje.')
                connection.close()
                return

        et = time.time()
        print(et-st)

        query = db.pax_engine.connect().execute(text(
            f'SELECT COUNT(*) FROM countries WHERE NOT country_id BETWEEN 253 AND 255')).fetchone()
        pages = []
        for x in range(int(query[0])):
            embed = await build_country_embed(self, str(x + 1))
            print(str(x+1))
            pages.append(Page(embeds=embed))
        print(country_id)
        await Paginator(
            client=self.bot,
            ctx=ctx,
            author_only=True,
            timeout=300,
            message="test",
            index=country_id[0]-1,
            pages=pages
        ).run()
