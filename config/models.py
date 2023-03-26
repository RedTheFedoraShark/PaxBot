import interactions


def info_command_map():
    author = interactions.EmbedAuthor(name="[] - Wymagane, () - Opcjonalne, {} - Dla adminów",
                                      icon_url="https://i.imgur.com/4MFkrcH.png")
    fb = interactions.EmbedField(name="", value="", inline=False)
    f1 = interactions.EmbedField(name="[mapa]", value=f"```ansi"
                                                      f"\n\u001b[0;31mProwincji\u001b[0;0m"
                                                      f"\n321 kolorowych prowincji."
                                                      f"\n\u001b[0;31mRegionów\u001b[0;0m"
                                                      f"\n30 regionów zeonici."
                                                      f"\n\u001b[0;31mZasobów\u001b[0;0m"
                                                      f"\n29 różnych zasobów."
                                                      f"\n\u001b[0;31mPolityczna\u001b[0;0m"
                                                      f"\nWasze świetne państwa."
                                                      f"\n\u001b[0;31mReligii\u001b[0;0m"
                                                      f"\nReligie wasze i nasze."
                                                      f"\n\u001b[0;31mPopulacji\u001b[0;0m"
                                                      f"\nPopulacje prowincji."
                                                      f"\n\u001b[0;31mAutonomii\u001b[0;0m"
                                                      f"\nAutnomie prowincji."
                                                      f"\n\u001b[0;31mPusta\u001b[0;0m"
                                                      f"\nPuste płótno.```", inline=True)
    f2 = interactions.EmbedField(name="[kontury]", value=f"```ansi"
                                                         f"\n\u001b[0;32mNie\u001b[0;0m"
                                                         f"\nBez konturów."
                                                         f"\n\u001b[0;32mTak\u001b[0;0m"
                                                         f"\nZ konturami.```", inline=True)
    f3 = interactions.EmbedField(name="[adnotacje]", value=f"```ansi"
                                                           f"\n\u001b[0;33mŻadne\u001b[0;0m"
                                                           f"\nBrak adnotacji."
                                                           f"\n\u001b[0;33mID Prowincji\u001b[0;0m"
                                                           f"\nNumery prowincji."
                                                           f"\n\u001b[0;33mNazwy Prowincji\u001b[0;0m"
                                                           f"\nNazwy waszych prowincji."
                                                           f"\n\u001b[0;33mNazwy Regionów\u001b[0;0m"
                                                           f"\nNazwy regionów Zeonici."
                                                           f"\n\u001b[0;33mNazwy Państw\u001b[0;0m"
                                                           f"\nNazwy waszych państw."
                                                           f"\n\u001b[0;33mArmie\u001b[0;0m"
                                                           f"\nAdnotacje armii.```", inline=True)
    f4 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\u001b[0;34madmin\u001b[0;0m"
                                                       f"\nPokazuje wszystkie możliwe informacje.```",
                                 inline=True)
    embed = interactions.Embed(
        title="/map [mapa] [kontury] [adnotacje] {admin}",
        description="Za pomocą tej komendy możesz wygenerować sobie własną mapę Zeonici!"
                    "\nNiektóre mapy mają informacje przeznaczone tylko dla gracza który wysyła komendę, "
                    "więc uważaj na publicznych kanałach!",
        author=author,
        fields=[f1, f3, fb, f2, f4]
    )
    return embed


def info_command_army():
    author = interactions.EmbedAuthor(name="[] - Wymagane, () - Opcjonalne, {} - Dla adminów",
                                      icon_url="https://i.imgur.com/4MFkrcH.png")
    fb = interactions.EmbedField(name="", value="", inline=False)
    f1 = interactions.EmbedField(name="[mapa]", value=f"```ansi"
                                                      f"\n\u001b[0;31mPusta\u001b[0;0m"
                                                      f"\nPuste płótno.```", inline=True)
    embed = interactions.Embed(
        title="/army list",
        description="Army List",
        author=author,
        fields=[f1]
    )
    return embed
