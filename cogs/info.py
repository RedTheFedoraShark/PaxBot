import interactions
import datetime
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
    async def kraj(self, ctx: interactions.CommandContext, country_name: str):
        # If string is a player ID.
        if country_name.endswith(">") and country_name.startswith("<"):
            cn = country_name.replace("<", "").replace("@", "").replace(">", "")
            result = db.pax_engine.connect().execute(text(
                f"SELECT * FROM players WHERE player_id = {cn}"))
            result = result.fetchall()
            print(country_name)
            print(result)
        connection = db.pax_engine.connect()
        if country_name.startswith('<@') and country_name.endswith('>'):  # if a ping
            # id = panstwo[2:-1]
            result = connection.execute(text(
                f'SELECT country_name FROM players NATURAL JOIN countries WHERE player_id = {country_name[2:-1]}')).fetchone()
            if result is None:
                await ctx.send('Ten gracz nie ma przypisanego państwa.')
                connection.close()
                return
            country_name = result[0]
        else:  # If string is (hopefully) a country name.
            result = connection.execute(
                text(f'SELECT country_name FROM countries WHERE country_name = "{country_name}"')).fetchone()
        await ctx.send(f"Kraj: {country_name}")

