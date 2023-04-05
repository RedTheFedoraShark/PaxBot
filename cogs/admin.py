import interactions
from sqlalchemy import text
from database import *
import pandas as pd
import numpy as np


def setup(bot):
    Admin(bot)


class Admin(interactions.Extension):
    def __init__(self, bot):
        self.bot = bot

    @interactions.extension_command(description="Testuj", scope='917078941213261914')
    async def admin(self, ctx: interactions.CommandContext):
        return

    @admin.subcommand(description="Zakończ obecną turę i rozpocznij kolejną.")
    async def endturn(self, ctx: interactions.CommandContext):
        connection = db.pax_engine.connect()
        income = []
        # Opening a loop for provinces ID 1-250
        for province_id in range(1, 251):
            # 1.1 Grabbing modifiers for the province (pops, autonomy and terrains)
            query = connection.execute(
                text(f"SELECT SUM(building_workers * quantity), province_pops, province_autonomy, terrain_id, "
                     f"country_id "
                     f"FROM provinces NATURAL JOIN structures NATURAL JOIN buildings "
                     f"WHERE province_id = {province_id}")).fetchone()
            if query[0] is None and query[4] in (253, 254, 255):
                continue
            elif query[0] is None:
                # 1.2 I love the IRS :)
                autonomy_modifier = (100 - query[2]) / 100
                income.append((query[4], 2, (int(query[1]) * 0.25) * autonomy_modifier))
                continue
            print(query)
            population_modifier = query[1] / int(query[0])
            if population_modifier > 1:
                population_modifier = 1
            autonomy_modifier = (100 - query[2]) / 100
            print(population_modifier, autonomy_modifier)
            # 1.2 I love the IRS :)
            income.append((query[4], 2, (int(query[1]) * 0.25) * autonomy_modifier))
            # 1.3 Bierzemy budynki jakie są w prowincji (typ budynku, ilość) i zbieramy info o ich przychodzie
            # (typ itemu, ilość) oraz modyfikator terenu
            query2 = connection.execute(
                text(f"SELECT building_id, quantity, item_id, item_quantity, modifier "
                     f"FROM provinces NATURAL JOIN structures NATURAL JOIN buildings NATURAL JOIN buildings_production "
                     f"NATURAL JOIN terrains_modifiers "
                     f"WHERE terrain_id={query[3]}")).fetchall()
            print(query2)
            # Liczymy produkcję dla danego typu budynku, w danej prowincji
            # production_quantity = ilość_budynków * (produkcja_budynku * (mod_populacji * mod_autonomii * mod_terenu))
            # production_quantity = 3 * (10 * (0.785 * 0.5 * 1.5))
            for row in query2:
                terrain_modifier = (100 + row[4]) / 100
                print(terrain_modifier)
                if row[3] < 0:
                    production_quan = row[3]
                else:
                    production_quan = row[1] * (row[3] * (population_modifier * autonomy_modifier * terrain_modifier))
                income.append((query[4], row[2], production_quan))
        print(income)
        # Sum up the quantities of items
        items = set()
        for x in income:
            items.add((x[0], x[1]))
        final_income = set()
        for x in items:
            final_income.add((x[0], x[1], round(sum(a[2] for a in income if a[0] == x[0] and a[1] == x[1]))))
        final_income = sorted(final_income)
        print(final_income)
        # ECONOMY ENDS HERE, THE REST IS LOGGING
        # income == [(2, -5), (4, 18), (2, -10), (3, 4)]
        # Po zamknięciu loopa dodajemy sumujemy wszystkie elementy które mają ten sam index=0 i commitujemy do bazy
        # production_sorted == [(2, -15), (4, 18), (3, 4)]
        countries = connection.execute(text(f"SELECT country_name FROM countries")).fetchall()
        items = connection.execute(text(f"SELECT item_name FROM items")).fetchall()
        countries = np.rot90(np.array(countries)).tolist()
        items = np.rot90(np.array(items)).tolist()
        print(countries, type(countries))
        print(items, type(items))
        inventories = connection.execute(text(f"SELECT country_id, item_id, quantity FROM inventories")).fetchall()
        inventories = pd.DataFrame(inventories)
        # inventories['combined'] = list(zip(inventories.country_id, inventories.item_id))
        print(inventories)
        final_table = []

        for x in final_income:
            if x[2] < 0:
                q = f"\u001b[0;31m-{x[2]}\u001b[0;0m"
            elif x[2] > 0:
                q = f"\u001b[0;32m+{x[2]}\u001b[0;0m"
            else:
                q = f"\u001b[0;33m{x[2]}\u001b[0;0m"

            final_table.append((countries[0][x[0]-1], items[0][x[1]-1], q))

        df = pd.DataFrame(final_table, columns=['Kraj', 'Item', 'Ilość'])
        print(df)
        embed = interactions.Embed(description='```ansi\n' + df.to_markdown(index=False) + '```')
        connection.close()
        await ctx.send(embeds=embed)
