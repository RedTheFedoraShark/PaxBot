import interactions
from sqlalchemy import text
from database import *
import pandas as pd
import numpy as np
from cogs import province


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
        # Opening a loop and getting income for provinces ID 1-250
        for province_id in range(1, 251):
            province.province_income(income, province_id)
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
        connection.close()
        await ctx.send(f"```ansi\n{df.to_markdown(index=False)}```")
