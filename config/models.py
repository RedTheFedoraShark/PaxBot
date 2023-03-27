import interactions


def commands():
    author = interactions.EmbedAuthor(name="[] - Wymagane, () - Opcjonalne, {} - Dla adminów",
                                      icon_url="https://i.imgur.com/4MFkrcH.png")
    fb = interactions.EmbedField(name="", value="", inline=False)
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
                                       f"\n\u001b[0;33m/army rename\u001b[0;0m"
                                       f"\nZmiana nazwy armii lub oddziału.```", inline=True)
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


def ic_tutorial():
    author = interactions.EmbedAuthor(name="[] - Wymagane, () - Opcjonalne, {} - Dla adminów",
                                      icon_url="https://i.imgur.com/4MFkrcH.png")
    fb = interactions.EmbedField(name="", value="", inline=False)
    f1 = interactions.EmbedField(name="[mapa]", value=f"```ansi"
                                                      f"\n\u001b[0;31mPusta\u001b[0;0m"
                                                      f"\nPuste płótno.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\u001b[0;35@ gracza lub nazwa kraju\u001b[0;0m"
                                                       f"\nPokazuje inventory danego kraju.```", inline=True)
    embed = interactions.Embed(
        title="/army list",
        description="Army List",
        author=author,
        fields=[f1]
    )
    return embed


def ic_commands():
    author = interactions.EmbedAuthor(name="[] - Wymagane, () - Opcjonalne, {} - Dla adminów",
                                      icon_url="https://i.imgur.com/4MFkrcH.png")
    fb = interactions.EmbedField(name="", value="", inline=False)
    f1 = interactions.EmbedField(name="[mapa]", value=f"```ansi"
                                                      f"\n\u001b[0;31mPusta\u001b[0;0m"
                                                      f"\nPuste płótno.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\u001b[0;35@ gracza lub nazwa kraju\u001b[0;0m"
                                                       f"\nPokazuje inventory danego kraju.```", inline=True)
    embed = interactions.Embed(
        title="/army list",
        description="Army List",
        author=author,
        fields=[f1]
    )
    return embed


def ic_info_command():
    author = interactions.EmbedAuthor(name="[] - Wymagane, () - Opcjonalne, {} - Dla adminów",
                                      icon_url="https://i.imgur.com/4MFkrcH.png")
    fb = interactions.EmbedField(name="", value="", inline=False)
    f1 = interactions.EmbedField(name="[mapa]", value=f"```ansi"
                                                      f"\n\u001b[0;31mPusta\u001b[0;0m"
                                                      f"\nPuste płótno.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\u001b[0;35@ gracza lub nazwa kraju\u001b[0;0m"
                                                       f"\nPokazuje inventory danego kraju.```", inline=True)
    embed = interactions.Embed(
        title="/army list",
        description="Army List",
        author=author,
        fields=[f1]
    )
    return embed


def ic_info_country():
    author = interactions.EmbedAuthor(name="[] - Wymagane, () - Opcjonalne, {} - Dla adminów",
                                      icon_url="https://i.imgur.com/4MFkrcH.png")
    fb = interactions.EmbedField(name="", value="", inline=False)
    f1 = interactions.EmbedField(name="[mapa]", value=f"```ansi"
                                                      f"\n\u001b[0;31mPusta\u001b[0;0m"
                                                      f"\nPuste płótno.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi"
                                                       f"\n\u001b[0;35@ gracza lub nazwa kraju\u001b[0;0m"
                                                       f"\nPokazuje inventory danego kraju.```", inline=True)
    embed = interactions.Embed(
        title="/army list",
        description="Army List",
        author=author,
        fields=[f1]
    )
    return embed


def ic_map():
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
                                                       f"\u001b[0;35madmin\u001b[0;0m"
                                                       f"\nPokazuje wszystkie możliwe informacje.```", inline=True)
    f5 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n"
                                       f"\u001b[0;40m/mapa [Polityczna] [Nie] [Armie]\u001b[0;0m```"
                                       f"\nGeneruje mapę z państwami graczy i armiami."
                                       f"\u001b[0;40m/mapa [Prowincji] [Tak] [ID Prowincji]\u001b[0;0m```"
                                       f"\nGeneruje mapę prowincji, konturami i ID prowincji.", inline=False)

    embed = interactions.Embed(
        title="/map [mapa] [kontury] [adnotacje] {admin}",
        description="Za pomocą tej komendy możesz wygenerować sobie własną mapę Zeonici!"
                    "\nNiektóre mapy mają informacje przeznaczone tylko dla gracza który wysyła komendę, "
                    "więc uważaj na publicznych kanałach!",
        author=author,
        fields=[f1, f3, fb, f2, f4, f5]
    )
    return embed


def ic_inventory_list():
    author = interactions.EmbedAuthor(name="[] - Wymagane, () - Opcjonalne, {} - Dla adminów",
                                      icon_url="https://i.imgur.com/4MFkrcH.png")
    fb = interactions.EmbedField(name="", value="", inline=False)
    f1 = interactions.EmbedField(name="[tryb]", value=f"```ansi"
                                                      f"\n\u001b[0;31mdokładny\u001b[0;0m"
                                                      f"\nInformacje w postaci szczegółowych stron."
                                                      f"\n\u001b[0;31mprosty\u001b[0;0m"
                                                      f"\nInformacje w postaci prostej listy.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi"
                                                       f"\n\u001b[0;35m@ gracza lub nazwa kraju\u001b[0;0m"
                                                       f"\nPokazuje inventory danego kraju.```", inline=True)
    f3 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi"
                                       f"\n\u001b[0;40m/inventory list [dokładny]\u001b[0;0m```"
                                       f"\nWyświela ekwipunek w postaci stron."
                                       f"\n\u001b[0;40m/inventory list [prosty]\u001b[0;0m```"
                                       f"\nWyświela ekwipunek w postaci listy.", inline=False)
    embed = interactions.Embed(
        title="/inventory list [tryb] {admin}",
        description="Placeholder.",
        author=author,
        fields=[f1, f2, f3]
    )
    return embed


def ic_inventory_items():
    author = interactions.EmbedAuthor(name="[] - Wymagane, () - Opcjonalne, {} - Dla adminów",
                                      icon_url="https://i.imgur.com/4MFkrcH.png")
    fb = interactions.EmbedField(name="", value="", inline=False)
    f1 = interactions.EmbedField(name="[mapa]", value=f"```ansi"
                                                      f"\n\u001b[0;31mPusta\u001b[0;0m"
                                                      f"\nPuste płótno.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\u001b[0;35@ gracza lub nazwa kraju\u001b[0;0m"
                                                       f"\nPokazuje inventory danego kraju.```", inline=True)
    embed = interactions.Embed(
        title="/army list",
        description="Army List",
        author=author,
        fields=[f1]
    )
    return embed


def ic_inventory_give():
    author = interactions.EmbedAuthor(name="[] - Wymagane, () - Opcjonalne, {} - Dla adminów",
                                      icon_url="https://i.imgur.com/4MFkrcH.png")
    fb = interactions.EmbedField(name="", value="", inline=False)
    f1 = interactions.EmbedField(name="[mapa]", value=f"```ansi"
                                                      f"\n\u001b[0;31mPusta\u001b[0;0m"
                                                      f"\nPuste płótno.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\u001b[0;35@ gracza lub nazwa kraju\u001b[0;0m"
                                                       f"\nPokazuje inventory danego kraju.```", inline=True)
    embed = interactions.Embed(
        title="/army list",
        description="Army List",
        author=author,
        fields=[f1]
    )
    return embed


def ic_army_list():
    author = interactions.EmbedAuthor(name="[] - Wymagane, () - Opcjonalne, {} - Dla adminów",
                                      icon_url="https://i.imgur.com/4MFkrcH.png")
    fb = interactions.EmbedField(name="", value="", inline=False)
    f1 = interactions.EmbedField(name="[mapa]", value=f"```ansi"
                                                      f"\n\u001b[0;31mPusta\u001b[0;0m"
                                                      f"\nPuste płótno.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\u001b[0;35@ gracza lub nazwa kraju\u001b[0;0m"
                                                       f"\nPokazuje inventory danego kraju.```", inline=True)
    embed = interactions.Embed(
        title="/army list",
        description="Army List",
        author=author,
        fields=[f1]
    )
    return embed


def ic_army_templates():
    author = interactions.EmbedAuthor(name="[] - Wymagane, () - Opcjonalne, {} - Dla adminów",
                                      icon_url="https://i.imgur.com/4MFkrcH.png")
    fb = interactions.EmbedField(name="", value="", inline=False)
    f1 = interactions.EmbedField(name="[mapa]", value=f"```ansi"
                                                      f"\n\u001b[0;31mPusta\u001b[0;0m"
                                                      f"\nPuste płótno.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\u001b[0;35@ gracza lub nazwa kraju\u001b[0;0m"
                                                       f"\nPokazuje inventory danego kraju.```", inline=True)
    embed = interactions.Embed(
        title="/army list",
        description="Army List",
        author=author,
        fields=[f1]
    )
    return embed


def ic_army_recruit():
    author = interactions.EmbedAuthor(name="[] - Wymagane, () - Opcjonalne, {} - Dla adminów",
                                      icon_url="https://i.imgur.com/4MFkrcH.png")
    fb = interactions.EmbedField(name="", value="", inline=False)
    f1 = interactions.EmbedField(name="[mapa]", value=f"```ansi"
                                                      f"\n\u001b[0;31mPusta\u001b[0;0m"
                                                      f"\nPuste płótno.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\u001b[0;35@ gracza lub nazwa kraju\u001b[0;0m"
                                                       f"\nPokazuje inventory danego kraju.```", inline=True)
    embed = interactions.Embed(
        title="/army list",
        description="Army List",
        author=author,
        fields=[f1]
    )
    return embed


def ic_army_disband():
    author = interactions.EmbedAuthor(name="[] - Wymagane, () - Opcjonalne, {} - Dla adminów",
                                      icon_url="https://i.imgur.com/4MFkrcH.png")
    fb = interactions.EmbedField(name="", value="", inline=False)
    f1 = interactions.EmbedField(name="[mapa]", value=f"```ansi"
                                                      f"\n\u001b[0;31mPusta\u001b[0;0m"
                                                      f"\nPuste płótno.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\u001b[0;35@ gracza lub nazwa kraju\u001b[0;0m"
                                                       f"\nPokazuje inventory danego kraju.```", inline=True)
    embed = interactions.Embed(
        title="/army list",
        description="Army List",
        author=author,
        fields=[f1]
    )
    return embed


def ic_army_reorg():
    author = interactions.EmbedAuthor(name="[] - Wymagane, () - Opcjonalne, {} - Dla adminów",
                                      icon_url="https://i.imgur.com/4MFkrcH.png")
    fb = interactions.EmbedField(name="", value="", inline=False)
    f1 = interactions.EmbedField(name="[mapa]", value=f"```ansi"
                                                      f"\n\u001b[0;31mPusta\u001b[0;0m"
                                                      f"\nPuste płótno.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\u001b[0;35@ gracza lub nazwa kraju\u001b[0;0m"
                                                       f"\nPokazuje inventory danego kraju.```", inline=True)
    embed = interactions.Embed(
        title="/army list",
        description="Army List",
        author=author,
        fields=[f1]
    )
    return embed


def ic_army_rename():
    author = interactions.EmbedAuthor(name="[] - Wymagane, () - Opcjonalne, {} - Dla adminów",
                                      icon_url="https://i.imgur.com/4MFkrcH.png")
    fb = interactions.EmbedField(name="", value="", inline=False)
    f1 = interactions.EmbedField(name="[mapa]", value=f"```ansi"
                                                      f"\n\u001b[0;31mPusta\u001b[0;0m"
                                                      f"\nPuste płótno.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\u001b[0;35@ gracza lub nazwa kraju\u001b[0;0m"
                                                       f"\nPokazuje inventory danego kraju.```", inline=True)
    embed = interactions.Embed(
        title="/army list",
        description="Army List",
        author=author,
        fields=[f1]
    )
    return embed


def ic_building_list():
    author = interactions.EmbedAuthor(name="[] - Wymagane, () - Opcjonalne, {} - Dla adminów",
                                      icon_url="https://i.imgur.com/4MFkrcH.png")
    fb = interactions.EmbedField(name="", value="", inline=False)
    f1 = interactions.EmbedField(name="[mapa]", value=f"```ansi"
                                                      f"\n\u001b[0;31mPusta\u001b[0;0m"
                                                      f"\nPuste płótno.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\u001b[0;35@ gracza lub nazwa kraju\u001b[0;0m"
                                                       f"\nPokazuje inventory danego kraju.```", inline=True)
    embed = interactions.Embed(
        title="/army list",
        description="Army List",
        author=author,
        fields=[f1]
    )
    return embed


def ic_building_templates():
    author = interactions.EmbedAuthor(name="[] - Wymagane, () - Opcjonalne, {} - Dla adminów",
                                      icon_url="https://i.imgur.com/4MFkrcH.png")
    fb = interactions.EmbedField(name="", value="", inline=False)
    f1 = interactions.EmbedField(name="[mapa]", value=f"```ansi"
                                                      f"\n\u001b[0;31mPusta\u001b[0;0m"
                                                      f"\nPuste płótno.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\u001b[0;35@ gracza lub nazwa kraju\u001b[0;0m"
                                                       f"\nPokazuje inventory danego kraju.```", inline=True)
    embed = interactions.Embed(
        title="/army list",
        description="Army List",
        author=author,
        fields=[f1]
    )
    return embed


def ic_building_build():
    author = interactions.EmbedAuthor(name="[] - Wymagane, () - Opcjonalne, {} - Dla adminów",
                                      icon_url="https://i.imgur.com/4MFkrcH.png")
    fb = interactions.EmbedField(name="", value="", inline=False)
    f1 = interactions.EmbedField(name="[mapa]", value=f"```ansi"
                                                      f"\n\u001b[0;31mPusta\u001b[0;0m"
                                                      f"\nPuste płótno.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\u001b[0;35@ gracza lub nazwa kraju\u001b[0;0m"
                                                       f"\nPokazuje inventory danego kraju.```", inline=True)
    embed = interactions.Embed(
        title="/army list",
        description="Army List",
        author=author,
        fields=[f1]
    )
    return embed


def ic_building_destroy():
    author = interactions.EmbedAuthor(name="[] - Wymagane, () - Opcjonalne, {} - Dla adminów",
                                      icon_url="https://i.imgur.com/4MFkrcH.png")
    fb = interactions.EmbedField(name="", value="", inline=False)
    f1 = interactions.EmbedField(name="[mapa]", value=f"```ansi"
                                                      f"\n\u001b[0;31mPusta\u001b[0;0m"
                                                      f"\nPuste płótno.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\u001b[0;35@ gracza lub nazwa kraju\u001b[0;0m"
                                                       f"\nPokazuje inventory danego kraju.```", inline=True)
    embed = interactions.Embed(
        title="/army list",
        description="Army List",
        author=author,
        fields=[f1]
    )
    return embed


def ic_building_upgrade():
    author = interactions.EmbedAuthor(name="[] - Wymagane, () - Opcjonalne, {} - Dla adminów",
                                      icon_url="https://i.imgur.com/4MFkrcH.png")
    fb = interactions.EmbedField(name="", value="", inline=False)
    f1 = interactions.EmbedField(name="[mapa]", value=f"```ansi"
                                                      f"\n\u001b[0;31mPusta\u001b[0;0m"
                                                      f"\nPuste płótno.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\u001b[0;35@ gracza lub nazwa kraju\u001b[0;0m"
                                                       f"\nPokazuje inventory danego kraju.```", inline=True)
    embed = interactions.Embed(
        title="/army list",
        description="Army List",
        author=author,
        fields=[f1]
    )
    return embed


def ic_province_list():
    author = interactions.EmbedAuthor(name="[] - Wymagane, () - Opcjonalne, {} - Dla adminów",
                                      icon_url="https://i.imgur.com/4MFkrcH.png")
    fb = interactions.EmbedField(name="", value="", inline=False)
    f1 = interactions.EmbedField(name="[mapa]", value=f"```ansi"
                                                      f"\n\u001b[0;31mPusta\u001b[0;0m"
                                                      f"\nPuste płótno.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\u001b[0;35@ gracza lub nazwa kraju\u001b[0;0m"
                                                       f"\nPokazuje inventory danego kraju.```", inline=True)
    embed = interactions.Embed(
        title="/army list",
        description="Army List",
        author=author,
        fields=[f1]
    )
    return embed


def ic_province_rename():
    author = interactions.EmbedAuthor(name="[] - Wymagane, () - Opcjonalne, {} - Dla adminów",
                                      icon_url="https://i.imgur.com/4MFkrcH.png")
    fb = interactions.EmbedField(name="", value="", inline=False)
    f1 = interactions.EmbedField(name="[mapa]", value=f"```ansi"
                                                      f"\n\u001b[0;31mPusta\u001b[0;0m"
                                                      f"\nPuste płótno.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\u001b[0;35@ gracza lub nazwa kraju\u001b[0;0m"
                                                       f"\nPokazuje inventory danego kraju.```", inline=True)
    embed = interactions.Embed(
        title="/army list",
        description="Army List",
        author=author,
        fields=[f1]
    )
    return embed
