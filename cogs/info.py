import interactions
from database import *
from sqlalchemy import text


def setup(bot):
    Info(bot)


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
        # If string is a player ID.
        connection = db.pax_engine.connect()
        print(c_input)
        if c_input.startswith('<@') and c_input.endswith('>'):  # if a ping
            # id = c_input[2:-1]
            result_countries = connection.execute(text(
                f'SELECT * FROM players NATURAL JOIN countries WHERE player_id = {c_input[2:-1]}')).fetchone()
            if result_countries is None:
                await ctx.send('Ten gracz nie ma przypisanego państwa.')
                connection.close()
                return
        else:  # If string is (hopefully) a country name.
            result_countries = connection.execute(
                text(f'SELECT * FROM players NATURAL JOIN countries WHERE country_name = "{c_input}"')).fetchall()
            if result_countries is None:
                await ctx.send('Takie państwo nie istnieje.')
                connection.close()
                return
            # Checking for multiple players
            if len(result_countries) == 1:
                return
            else:
                names = ''
                for x in result_countries:
                    names = f"{names} {x[2]}"
                result_countries = list(result_countries[0])
                result_countries[2] = names
        print(result_countries)
        # Embed items
        user = await interactions.get(
            self.bot, interactions.User, object_id=result_countries[1])
        pop_sum = connection.execute(text(
            f"SELECT SUM(province_pops) FROM provinces WHERE country_id = {result_countries[0]}")).fetchone()
        capital = connection.execute(text(
            f"SELECT province_name FROM provinces WHERE province_id = {result_countries[10]}")).fetchone()
        province_sum = connection.execute(text(
            f"SELECT COUNT(*) FROM provinces WHERE country_id = {result_countries[0]}")).fetchone()
        religion = connection.execute(text(
            f"SELECT religion_name FROM religions WHERE religion_id = {result_countries[9]}")).fetchone()
        # autonomy = connection.execute(text(
        #   f"SELECT COUNT(*),SUM(province_autonomy) FROM provinces WHERE country_id={result_countries[0]}")).fetchone()
        # autonomy = f"{autonomy[1] / autonomy[0]}%"

        embed_footer = interactions.EmbedFooter(
            text=result_countries[13],
            icon_url=result_countries[14]
        )
        embed_thumbnail = interactions.EmbedImageStruct(
            url=result_countries[12],
            height=100,
            width=100
        )
        embed_author = interactions.EmbedAuthor(
            name=result_countries[2],
            icon_url=user.avatar_url
        )
        fb = interactions.EmbedField(name="", value="", inline=False)
        f1 = interactions.EmbedField(name="Władca", value=result_countries[7], inline=True)
        f2 = interactions.EmbedField(name="Ustrój", value=result_countries[8], inline=True)
        f3 = interactions.EmbedField(name="Stolica", value=f"{capital[0]} ({result_countries[10]})", inline=True)
        f4 = interactions.EmbedField(name="Domena", value=f"{province_sum[0]} prowincji.", inline=True)
        f5 = interactions.EmbedField(name="Religia", value=religion[0], inline=True)
        f6 = interactions.EmbedField(name="Populacja", value=f"{pop_sum[0]} osób.", inline=True)
        # f7 = interactions.EmbedField(name="Autonomia", value=autonomy, inline=True)
        f8 = interactions.EmbedField(name="Dyplomacja", value="<#1084509996106137632>", inline=True)
        f9 = interactions.EmbedField(name="Wydarzenia", value="<#1064216866798710904>", inline=True)

        # Building the Embed
        embed = interactions.Embed(
            color=int(result_countries[6], 16),
            title=result_countries[4],
            # description=result_countries[5],
            url=result_countries[11],
            footer=embed_footer,
            thumbnail=embed_thumbnail,
            author=embed_author,
            fields=[f1, f2, fb, f3, f4, fb, f5, f6, fb, f8, f9]
        )
        await ctx.send(embeds=embed)

