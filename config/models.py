import interactions

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


def ic_inventory_items():
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
                                                          f"\n\u001b[0;32m•Item i ilość\u001b[0;0m"
                                                          f"\nRodzaj i ilość itemów które chcemy dać.```", inline=True)
    f3 = interactions.EmbedField(name="{admin}", value=f"```ansi"
                                                       f"\n\u001b[0;35m•admin\u001b[0;0m"
                                                       f"\nPozwala na spawnowanie itemów.```", inline=True)
    f4 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/inventory give [@XnraD] [10 Talary]\u001b[0;0m```"
                                       f"\nDaje państwu XnraD'a (Karbadia) 10 talarów."
                                       f"```ansi\n\u001b[0;40m/inventory give [@XnraD] [15 Drewno,"
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
                                 value=f"```ansi\n\u001b[0;40m/inventory list [Dokładny]\u001b[0;0m```"
                                       f"\nWyświela armie w postaci stron."
                                       f"```ansi\n\u001b[0;40m/inventory list [Prosty]\u001b[0;0m```"
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
        title="/army template (jednostka) {admin}",
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
                                                           f"\nZ prowincji o ten nazwie będzie pochodzić jednostka.```"
                                 , inline=True)
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
                                       f"(Pierwsza Chorągiew Karbadii)\u001b[0;0m```"
                                       f"\nTo samo co wyżej, ale na dodatek ustawia nazwę jednostki oraz nazwę armii co"
                                       f" ułatwia jej przyszłe zarządzanie i dodaje nam rigczu na polu bitwy."
                                 , inline=False)
    embed = interactions.Embed(
        title="/army recruit [prowincja] [jednostka] (nazwa_jednostki) (nazwa_armii) {admin}",
        description="Rekrutuje daną jednostkę w danej prowincji.\n"
                    "Pobiera potrzebną ilość populacji z rekrutowanej prowincji.\n"
                    "Nazwy jednostek ani armii nie mogą się duplikować.",
        author=author,
        fields=[f1, f5, fb, f2, f3, f4, f6]
    )
    return embed


def ic_army_disband():
    f1 = interactions.EmbedField(name="[jednostka]", value=f"```ansi"
                                                           f"\n\u001b[0;31m•# jednostki\u001b[0;0m"
                                                           f"\nRozwiązuje jednostkę o danym ID."
                                                           f"\n\u001b[0;31m•Nazwa jednostki\u001b[0;0m"
                                                           f"\nRozwiązuje jednostkę o danej nazwie.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi"
                                                       f"\n\u001b[0;35m•@ gracza\u001b[0;0m"
                                                       f"\nUsuwa jednostkę krajowi danego gracza."
                                                       f"\n\u001b[0;35m•Nazwa Kraju\u001b[0;0m"
                                                       f"\nUsuwa jednostkę danemu krajowi.```", inline=True)
    f3 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/army disband [Gwardia Królewska]\u001b[0;0m```"
                                       f"\nRozwiązuje jednostkę."
                                       f"\nZwraca część kosztów rekrutacyjnych oraz żywych żołnierzy do "
                                       f"prowincji ich pochodzenia.", inline=False)
    embed = interactions.Embed(
        title="/army disband [jednostka] {admin}",
        description="Rozwiązuje daną jednostkę zwracając część surowców i odsyłając wojów do domu.\n"
                    "Populacja pobrana podczas rekrutacji wraca do swojej prowincji.\n"
                    "Możesz rozwiązać armie tylko w granicach swojego państwa.",
        author=author,
        fields=[f1, f2, f3]
    )
    return embed


def ic_army_reorg():
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


def ic_army_resupply():
    f1 = interactions.EmbedField(name="[jednostka]", value=f"```ansi"
                                                           f"\n\u001b[0;31m•# jednostki\u001b[0;0m"
                                                           f"\nRozwiązuje jednostkę o danym ID."
                                                           f"\n\u001b[0;31m•Nazwa jednostki\u001b[0;0m"
                                                           f"\nRozwiązuje jednostkę o danej nazwie.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\u001b[0;35@ gracza lub nazwa kraju\u001b[0;0m"
                                                       f"\nPokazuje inventory danego kraju.```", inline=True)
    f3 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/army resupply [Gwardia Królewska]\u001b[0;0m```"
                                       f"\nPrzywraca jednostkę 'Gwardia Królewska' do pełni sił."
                                       f"\nGdyby przedtem miała tylko 75% stanu osobowego z powodu bitew lub innych "
                                       f"powodów, teraz wróciła by do 100% sił."
                                       f"\nOdejęte zostanie również 25% bazowego kosztu jednostki z inventory kraju."
                                 , inline=False)
    embed = interactions.Embed(
        title="/army resupply [jednostka] {admin}",
        description="Przywraca uszkodzoną jednostkę do pełnej gotowości bojowej.\n"
                    "Pobiera odpowiednią ilość surowców zależną od stopnia uszkodzenia i bazowego kosztu jednostki.",
        author=author,
        fields=[f1, f2, f3]
    )
    return embed


def ic_army_rename():
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
