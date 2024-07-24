import random
import interactions
import json
import re

import numpy
import numpy as np
import pandas as pd
from database import *
from sqlalchemy import text
import roman

with open("./config/config.json") as f:
    configure = json.load(f)


class Income:
    def __init__(self, pops: float, buildings_incomes: dict, hunger: float = 0, country_id: int = 0,
                 controller_id: int = 0):
        self.pops = pops
        self.hunger = hunger
        self.country_id = country_id
        self.controller_id = controller_id
        self.buildings_incomes = buildings_incomes

    def __str__(self):
        return (f"Income(pops={self.pops}, hunger={self.hunger}, country_id={self.country_id}, "
                f"controller_id={self.controller_id}, buildings_incomes={self.buildings_incomes})")

        # Create an author element with country info for an embed


async def country_author(self, country_id: int):
    connection = db.pax_engine.connect()
    query = connection.execute(text(
        f"""SELECT 
                  c.country_id,
                  c.country_name,
                  p.player_id,
                  c.country_image_url,
                  c.country_bio_url
                FROM 
                  countries c
                  NATURAL JOIN players p
                WHERE 
                  c.country_id = {country_id};
              """)).all()
    if not query:
        return
    owners = ''
    for row in query:
        member = await self.bot.fetch_member(user_id=row[2], guild_id=configure['GUILD'])
        user = member.user
        owners = f"{user.tag} {owners}"

    country_id, country_name, player_id, country_image_url, country_bio_url = query[0]

    return interactions.EmbedAuthor(name=f'{country_name}, {owners}', icon_url=country_image_url, url=country_bio_url)


# Pagify a table string
def pagify(dataframe: list, max_char: int):
    # print(dataframe)
    bit = ''
    bits = []
    # print(len(dataframe))
    for i, line in enumerate(dataframe):
        if len(bit) + len(line) > max_char:
            bits.append(bit)
            bit = ''
        bit = f"{bit}\n{line}"
        # print(i)
        # print(bit)
        if i == len(dataframe) - 1:
            bits.append(bit)

    return bits


def get_province_modifiers(province_id):
    connection = db.pax_engine.connect()
    # 1. Grabbing modifiers for the province (pops, terrains)
    # 1.1 Pops
    q = connection.execute(text(
        f"SELECT province_pops, country_id, controller_id FROM provinces WHERE province_id = {province_id}"
    )).fetchone()
    if not q:
        pops, country_id, controller_id = 0, 0, 0
    else:
        pops, country_id, controller_id = q

    # 1.2 Terrain
    q = connection.execute(
        text(f"SELECT tm.building_id, tm.throughput_modifier, tm.input_modifier, tm.output_modifier "
             f"FROM provinces p NATURAL JOIN terrains t NATURAL JOIN terrains_modifiers tm "
             f"WHERE province_id = {province_id}")).fetchall()
    if not q:  # No terrain modifiers, this should not happen ever
        raise Exception('There are no terrain modifiers in your database. Add them, they can be blank.')
    terrain_modifiers = {}
    for tm in q:
        building_id, throughput_modifier, input_modifier, output_modifier = tm
        terrain_modifiers[building_id] = throughput_modifier, input_modifier, output_modifier  # 2: 10, -10, 20

    # 1.3 Workforce

    q = connection.execute(
        text(f"SELECT SUM(b.building_workers * s.quantity) "
             f"FROM provinces p LEFT "
             f"JOIN structures s ON p.province_id = s.province_id LEFT "
             f"JOIN buildings b ON s.building_id = b.building_id "
             f"WHERE p.province_id = {province_id}")).fetchone()
    if not q[0]:  # No buildings with income
        total_workers = 0
        workforce_modifier = 0
    else:
        total_workers = q[0]
        if total_workers == 0:  # Don't divide by zero
            total_workers = 1
        workforce_modifier = pops / int(total_workers)  # (0 ; 1)
        workforce_modifier = workforce_modifier
        if workforce_modifier > 1:
            workforce_modifier = 1
    return total_workers, pops, workforce_modifier, terrain_modifiers, country_id, controller_id


# Calculate the income of every building and assign them to a province
# Output: {province_id: [taxes, [building_id: [building_id, quantity, building_name, building_emoji, workforce_modifier,
# building_workers [item_id: [item_name, item_emoji, quantity], [item_id: [item_name, item_emoji, quantity], ...]]]]...}
def get_provinces_incomes():
    connection = db.pax_engine.connect()

    # Get info about all provinces
    q = connection.execute(
        text(
            f"""
SELECT 
  p.province_id, 
  p.country_id, 
  p.controller_id, 
  p.terrain_id, 
  p.province_pops AS pops, 
  IFNULL(
    SUM(b.building_workers * s.quantity), 
    0
  ) AS workers, 
  IF(IFNULL(
    p.province_pops / IFNULL(
      SUM(b.building_workers * s.quantity), 
      0
    ), 
    0
  ) > 1, 1, IFNULL(
    p.province_pops / IFNULL(
      SUM(b.building_workers * s.quantity), 
      0
    ), 
    0
  )) AS workforce_modifier
FROM 
  provinces p 
  LEFT JOIN structures s ON p.province_id = s.province_id 
  LEFT JOIN buildings b ON s.building_id = b.building_id 
GROUP BY 
  p.province_id
ORDER BY 
  p.province_id
        """)).fetchall()
    # +-------------+------------+---------------+------------+------+---------+--------------------+
    # | province_id | country_id | controller_id | terrain_id | pops | workers | workforce_modifier |
    # +-------------+------------+---------------+------------+------+---------+--------------------+
    # |           1 |        255 |           255 |          6 | 1.00 |       0 |           0.000000 |
    # |           2 |        255 |           255 |          3 | 1.00 |       0 |           0.000000 |
    # |           3 |        255 |           255 |          3 | 1.00 |       0 |           0.000000 |
    if not q:  # This shouldn't happen ever. If it does, add provinces to the database.
        raise Exception('There are no provinces in your database.')
    provinces = q

    # Get all terrain modifiers
    q = connection.execute(
        text(
            f"""
SELECT 
  tm.terrain_id,
  tm.building_id, 
  tm.throughput_modifier, 
  tm.input_modifier, 
  tm.output_modifier 
FROM 
  terrains_modifiers tm 
        """)).fetchall()
    # +------------+-------------+---------------------+----------------+-----------------+
    # | terrain_id | building_id | throughput_modifier | input_modifier | output_modifier |
    # +------------+-------------+---------------------+----------------+-----------------+
    # |          1 |           1 |                   0 |              0 |               0 |
    # |          1 |           2 |                   0 |              0 |               0 |
    # |          1 |           3 |                   0 |              0 |               0 |
    if not q:  # This shouldn't happen ever.
        # If it does, cross join [terrains] and [buildings] and input it into the database.
        raise Exception('There are no terrain modifiers in your database.')
    tm = q
    terrain_modifiers = np.array(tm, dtype='O')

    # Get all structures built
    q = connection.execute(
        text(
            f"""
SELECT 
  p.province_id, 
  b.building_id, 
  s.quantity, 
  b.building_name, 
  b.building_emoji, 
  b.building_workers 
FROM 
  provinces p NATURAL 
  JOIN buildings b NATURAL 
  JOIN structures s;
        """)).fetchall()
    # +-------------+-------------+----------+---------------+----------------------------------+------------------+
    # | province_id | building_id | quantity | building_name | building_emoji                   | building_workers |
    # +-------------+-------------+----------+---------------+----------------------------------+------------------+
    # |          50 |           1 |        1 | Tartak        | <:Tartak:1259978101442740327>    |                1 |
    # |          50 |           2 |        1 | Farma         | <:Farma:1259978050536345723>     |                1 |
    # |          50 |           3 |        1 | Kopalnia      | <:Kopalnia:1259978065988288624>  |                1 |
    all_buildings = pd.DataFrame(q,
                                 columns=['province_id', 'building_id', 'quantity', 'building_name', 'building_emoji',
                                          'building_workers'])

    # Get all buildings production
    q = connection.execute(
        text(
            f"""
SELECT 
  bp.building_id,
  bp.item_id, 
  bp.item_quantity, 
  i.item_name, 
  i.item_emoji 
FROM 
  buildings_production bp NATURAL 
  JOIN items i
                        """)).fetchall()
    # +-------------+---------+---------------+-------------------+------------------------------------------+
    # | building_id | item_id | item_quantity | item_name         | item_emoji                               |
    # +-------------+---------+---------------+-------------------+------------------------------------------+
    # |           1 |       4 |             3 | Drewno            | <:Drewno:1259246014292820058>            |
    # |           2 |       3 |             4 | Żywność           | <:Zywnosc:1259245985272561815>           |
    # |           3 |       5 |             2 | Kamień            | <:Kamien:1259246006990536764>            |
    buildings_production = np.array(q, dtype='O')

    # Get all inventories
    q = connection.execute(
        text(
            f"""
SELECT 
  item_id,
  country_id,
  quantity
FROM 
  inventories
                        """)).fetchall()
    # +---------+------------+----------+
    # | item_id | country_id | quantity |
    # +---------+------------+----------+
    # |       1 |          1 |     0.00 |
    # |       1 |          2 |     0.00 |
    # |       1 |        253 |     0.00 |
    inventories = pd.DataFrame(q, columns=['item_id', 'country_id', 'quantity'])

    province_incomes = {}
    all_incomes = []
    buildings_without_production = {}
    for province in provinces:
        province_id, country_id, controller_id, terrain_id, pops, workers, workforce_modifier = province
        buildings_without_production[province_id] = []

        # 2. Get province buildings
        province_buildings = all_buildings.loc[all_buildings['province_id'] == province_id]
        if province_buildings is None:
            return Income(pops, dict())

        # 3. Get production and apply modifiers
        resources = {}
        for i, building in province_buildings.iterrows():
            province_id, building_id, quantity, building_name, building_emoji, building_workers = building
            production = buildings_production[(buildings_production[:, 0] == building_id)]
            if production is None: continue
            province_terrain_modifiers = terrain_modifiers[(terrain_modifiers[:, 0] == terrain_id) &
                                                           (terrain_modifiers[:, 1] == building_id)]

            terrain_id, building_id, throughput_modifier, input_modifier, output_modifier = (
                province_terrain_modifiers)[0]  # [[2 2 0 0 0]]
            building_income = {}

            if len(production) == 0:
                buildings_without_production[province_id].append(
                    [province_id, building_id, quantity, building_name, building_emoji, building_workers])
            for income in production:
                building_id, item_id, item_quantity, item_name, item_emoji = income
                if item_quantity > 0:  # If income
                    item_quantity = (item_quantity * workforce_modifier * throughput_modifier * output_modifier)
                if item_quantity < 0:  # If cost
                    item_quantity = (item_quantity * workforce_modifier * throughput_modifier * input_modifier)

                if country_id != controller_id:  # Halve income if occupied
                    item_quantity = item_quantity / 2

                building_income[item_id] = [item_quantity, item_name, item_emoji]
                all_incomes.append(
                    [province_id, round(pops, 1), country_id, controller_id, building_id, quantity, building_name,
                     building_emoji, workforce_modifier, building_workers, building_income, item_id, item_quantity,
                     item_name, item_emoji])

            resources[building_id] = [quantity, building_name, building_emoji, workforce_modifier,
                                      building_workers, building_income]
        income = Income(pops=round(pops, 1), buildings_incomes=resources, country_id=country_id,
                        controller_id=controller_id)
        province_incomes[province_id] = income

    all_incomes = pd.DataFrame(all_incomes,
                               columns=['province_id', 'pops', 'country_id', 'controller_id', 'building_id', 'quantity',
                                        'building_name', 'building_emoji', 'workforce_modifier', 'building_workers',
                                        'building_income', 'item_id', 'item_quantity', 'item_name', 'item_emoji'])

    resources_modifiers = []
    for i, item in inventories.iterrows():
        item_id, country_id, stockpile = item
        summed_item_income = all_incomes.loc[
            (all_incomes['item_id'] == item_id) & (all_incomes['country_id'] == country_id) & (
                    all_incomes['item_quantity'] > 0), 'item_quantity'].sum()
        summed_item_used = all_incomes.loc[
            (all_incomes['item_id'] == item_id) & (all_incomes['country_id'] == country_id) & (
                    all_incomes['item_quantity'] < 0), 'item_quantity'].sum()
        if summed_item_used == 0:
            resources_modifiers.append([country_id, item_id, 1])
        elif (stockpile + summed_item_income) == 0:
            resources_modifiers.append([country_id, item_id, 0])
        else:
            modifier = (stockpile + summed_item_income) / abs(summed_item_used)
            if modifier > 1:
                modifier = 1
            resources_modifiers.append([country_id, item_id, modifier])
    for r_modifier in resources_modifiers:
        country_id, item_id, modifier = r_modifier
        if modifier == 1:
            continue
        building_ids = all_incomes.loc[
            (all_incomes['item_id'] == item_id) & (all_incomes['country_id'] == country_id) & (
                    all_incomes['item_quantity'] < 0), 'building_id']
        for row in building_ids.items():
            # (index, building_id)
            all_incomes.loc[(all_incomes['building_id'] == row[1]) & (
                    all_incomes['country_id'] == country_id), 'item_quantity'] *= modifier

    # Pack all of this into Incomes
    for province in provinces:
        province_id, country_id, controller_id, terrain_id, pops, workers, workforce_modifier = province

        province_buildings = all_incomes.loc[(all_incomes['province_id'] == province_id)]
        province_buildings = province_buildings[
            ['province_id', 'building_id', 'quantity', 'building_name', 'building_emoji', 'building_workers']]
        if buildings_without_production[province_id]:
            bwp = pd.DataFrame(buildings_without_production[province_id],
                               columns=['province_id', 'building_id', 'quantity', 'building_name', 'building_emoji',
                                        'building_workers'])
            province_buildings = pd.concat([province_buildings, pd.DataFrame(bwp)], ignore_index=True)
        resources = {}
        for i, building in province_buildings.iterrows():
            province_id, building_id, quantity, building_name, building_emoji, building_workers = building

            production = all_incomes.loc[
                (all_incomes['province_id'] == province_id) & (all_incomes['building_id'] == building_id)]
            production = production[['building_id', 'item_id', 'item_quantity', 'item_name', 'item_emoji']]
            building_income = {}
            for i, income in production.iterrows():
                building_id, item_id, item_quantity, item_name, item_emoji = income
                pos_item_quantity = 0
                neg_item_quantity = 0
                if item_quantity > 0:
                    pos_item_quantity += item_quantity
                else:
                    neg_item_quantity += item_quantity

                building_income[item_id] = [pos_item_quantity, neg_item_quantity, item_name, item_emoji]
            resources[building_id] = [quantity, building_name, building_emoji, workforce_modifier,
                                      building_workers, building_income]
        income = Income(pops=round(pops, 1), buildings_incomes=resources, country_id=country_id,
                        controller_id=controller_id)
        province_incomes[province_id] = income
    # >>> buildings_incomes
    # {
    #   1: [1, 'Tartak', '<:Tartak:1259978101442740327> ', 0.432727, 1, {
    #     4: [1.298181, 'Drewno', '<:Drewno:1259246014292820058>']
    #   }],
    #   3: [1, 'Kopalnia', '<:Kopalnia:1259978065988288624>', 0.432727, 1, {
    #     5: [0.865454, 'Kamień', '<:Kamien:1259246006990536764>']
    #   }],
    #   4: [1, 'Stadnina', ...
    # }

    connection.close()
    return province_incomes


# Input a dict of provinces with incomes and return a single dict of buildings with summed incomes
def sum_building_incomes(incomes: dict):
    total_pops = 0
    country_id = 0
    controller_id = 0

    for province_id in incomes:
        country_id = incomes[province_id].country_id

        controller_id = incomes[province_id].controller_id
        total_pops += incomes[province_id].pops

    building_keys = set()
    for province_id in incomes:
        for income_key in incomes[province_id].buildings_incomes:
            building_keys.add(income_key)

    buildings = {}
    for key in building_keys:
        buildings[key] = [0, "name", "emoji", 0, 0, {}]
        buildings[key] = {'quantity': 0, 'name': "name", 'emoji': "emoji", 'pops': 0, 'workers': 0,
                          'resource': {}}  # 39: [0.84, 'Cegły', '<:Cegly:1259246021746229248>']

    for province_id in incomes:

        for income_key in incomes[province_id].buildings_incomes:
            # print('\n')

            quantity, name, emoji, pops, workers, resource = incomes[province_id].buildings_incomes[income_key]
            # print(f'{quantity}  {workers}  {pops}')
            # print(income)
            buildings[income_key]['pops'] = ((buildings[income_key]['quantity'] * buildings[income_key]['pops']) + (
                    quantity * pops)) / (buildings[income_key]['quantity'] + quantity)
            buildings[income_key]['quantity'] = buildings[income_key]['quantity'] + quantity
            buildings[income_key]['name'] = name
            buildings[income_key]['emoji'] = emoji
            buildings[income_key]['workers'] = workers
            for r_key in resource:  # 39: [0.84, -0, 'Cegły', '<:Cegly:1259246021746229248>']
                if r_key in buildings[income_key]['resource']:
                    buildings[income_key]['resource'][r_key][0] = buildings[income_key]['resource'][r_key][
                                                                      0] + quantity * resource[r_key][0]
                    buildings[income_key]['resource'][r_key][1] = buildings[income_key]['resource'][r_key][
                                                                      1] + quantity * resource[r_key][1]
                else:
                    buildings[income_key]['resource'][r_key] = resource[r_key]
                    buildings[income_key]['resource'][r_key][0] = buildings[income_key]['resource'][r_key][0] * quantity
                    buildings[income_key]['resource'][r_key][1] = buildings[income_key]['resource'][r_key][1] * quantity

            buildings[income_key]['quantity'] = round(buildings[income_key]['quantity'], 1)

    incomes = Income(pops=total_pops, buildings_incomes=buildings, country_id=country_id,
                     controller_id=controller_id)
    return incomes


# Input a dict of provinces with incomes and return a single dict of provinces with summed incomes and no buildings
def sum_item_incomes(incomes: dict):
    total_pops = 0
    country_id = 0
    controller_id = 0

    for province_id in incomes:
        country_id = incomes[province_id].country_id

        controller_id = incomes[province_id].controller_id
        total_pops += incomes[province_id].pops
        #  incomes[province_id] = incomes[province_id].buildings_incomes

    item_keys = set()
    for province_id in incomes:
        for income_key in incomes[province_id].buildings_incomes:
            for item_key in incomes[province_id].buildings_incomes[income_key][5]:
                # [2, 'Tartak', '<:Tartak:1259978101442740327> ', 1.0, 1, {4: [6.0, -2.0, 'Drewno',
                # '<:Drewno:1259246014292820058>']}]
                item_keys.add(item_key)

    items = {}
    for key in item_keys:
        items[key] = {'pos_quantity': 0, 'neg_quantity': 0, 'name': 'name', 'emoji': 'emoji'}

    for province_id in incomes:
        for income_key in incomes[province_id].buildings_incomes:
            quantity, name, emoji, pops, workers, resource = incomes[province_id].buildings_incomes[income_key]

            for item_key in incomes[province_id].buildings_incomes[income_key][5]:
                items[item_key]['name'] = resource[item_key][2]
                items[item_key]['emoji'] = resource[item_key][3]
                items[item_key]['pos_quantity'] = items[item_key]['pos_quantity'] + resource[item_key][0] * quantity
                items[item_key]['neg_quantity'] = items[item_key]['neg_quantity'] + resource[item_key][1] * quantity

            for item_key in incomes[province_id].buildings_incomes[income_key][5]:
                items[item_key]['pos_quantity'] = round(items[item_key]['pos_quantity'], 1)
                items[item_key]['neg_quantity'] = round(items[item_key]['neg_quantity'], 1)

    incomes = Income(pops=total_pops, buildings_incomes=items, country_id=country_id,
                     controller_id=controller_id)

    return incomes


# Input a dictionary of provinces with pops and controller_id. Output a dict of 2 dicts: first with food economy
# of each country, second with an updated provinces dictionary with 'hunger' set.
def get_hunger(incomes: {int: Income}):
    connection = db.pax_engine.connect()
    countries = {}

    for province_id in incomes:
        countries[incomes[province_id].controller_id] = {'hunger': 1.0, 'pops_food_eaten': 0,
                                                         'pops_self_sustaining': 0, 'army_food_eaten': 0,
                                                         'food_produced': 0, 'country_food_reserves': 0}

    for country_id in countries:
        army_consumption = connection.execute(
            text(f"""
            SELECT SUM(um.item_quantity) 
            FROM armies a NATURAL 
            JOIN units_maintenance um 
            WHERE a.country_id = {country_id} 
            AND a.army_conscripted = 0 
            AND um.item_id = 3
            """)).fetchone()
        if not army_consumption[0]:
            army_consumption = 0
        else:
            army_consumption = float(army_consumption[0])
        countries[country_id]['army_food_eaten'] = army_consumption

        food_reserves = connection.execute(
            text(f"""
            SELECT quantity FROM inventories WHERE item_id = 3 AND country_id = {country_id}
            """)).fetchone()
        if not food_reserves:
            food_reserves = 0
        else:
            food_reserves = food_reserves[0]
        countries[country_id]['country_food_reserves'] = food_reserves

    for province_id in incomes:
        province_food_production = 0
        for item_id in incomes[province_id].buildings_incomes:
            if item_id == 3:
                province_food_production += incomes[province_id].buildings_incomes[item_id]['pos_quantity']
                province_food_production += incomes[province_id].buildings_incomes[item_id]['neg_quantity']

        if province_food_production >= incomes[province_id].pops:
            incomes[province_id].hunger = 1
            countries[incomes[province_id].controller_id]['pops_self_sustaining'] += incomes[province_id].pops

        countries[incomes[province_id].controller_id]['pops_food_eaten'] += incomes[province_id].pops
        countries[incomes[province_id].controller_id]['food_produced'] += province_food_production

    for country_id in countries:
        if countries[country_id]['pops_food_eaten'] + countries[country_id]['army_food_eaten'] == 0:
            countries[country_id]['hunger'] = 1
        else:
            countries[country_id]['hunger'] = (
                    (countries[country_id]['food_produced'] + countries[country_id]['country_food_reserves'] -
                     countries[country_id]['pops_self_sustaining']) /
                    (countries[country_id]['army_food_eaten'] + countries[country_id]['pops_food_eaten'] -
                     countries[country_id]['pops_self_sustaining']))

    for province_id in incomes:
        if incomes[province_id].hunger == 1:
            continue
        else:
            incomes[province_id].hunger = countries[incomes[province_id].controller_id]['hunger']

    connection.close()
    return {'countries': countries, 'hunger_incomes': incomes}


def get_buildings_income_description(buildings: dict):
    def makeline(desc: str, build_id: int):
        #print(buildings)
        #print(buildings[build_id])
        #print(buildings[build_id].items())
        quantity, name, emoji, workers, pops, incomes = buildings[build_id].values()
        if pops == 0:  # If the building doesn't use pops, don't add information about it to the line
            desc += f'\u2028{emoji} **{name} x{quantity}\n**'
        else:
            if workers == 1:  # Add an exclamation mark where there is not enough pop to work
                desc += (f'\u2028{emoji} **{name} x{quantity}**\n*[{round(workers * pops * quantity, 1)}'
                         f'/{round(pops * quantity, 1)}]* {round(workers * 100, 1)}%\n')
            else:
                desc += (f'\u2028{emoji} **{name} x{quantity}**\n*[{round(workers * pops * quantity, 1)}'
                         f'/{round(pops * quantity, 1)}]* {round(workers * 100, 1)}% :exclamation:\n')

        for i_key in incomes:
            pos_item_quantity, neg_item_quantity, name, emoji = incomes[i_key]
            item_quantity = pos_item_quantity + neg_item_quantity
            if item_quantity > 0:  # Assign an emoji indicator to income/cost
                desc += f'<:small_triangle_up:1260292468704809071> {emoji} `{round(item_quantity, 1)}` {name}\n'
            elif item_quantity == 0:
                desc += f':small_orange_diamond: {emoji} `{round(item_quantity, 1)}` {name}\n'
            else:
                desc += f'<:small_triangle_down:1260292467044122636> {emoji} `{round(item_quantity, 1)}` {name}\n'
        # desc += '\n'

        return desc

    connection = db.pax_engine.connect()

    production_building_ids = []
    military_building_ids = []
    special_building_ids = []
    for building_id in buildings:
        q = connection.execute(text(
            f"""SELECT 
                    country_id, building_workers
                FROM 
                    country_buildings NATURAL JOIN buildings 
                WHERE
                    building_id = {building_id}
                  """)).fetchone()
        if q is None: continue

        country_id, building_workers = q
        if country_id != 255:  # If building is special (Not default for every country. country_id == 255)
            special_building_ids.append(building_id)
        else:
            if building_workers == 0:  # If building has no workers
                military_building_ids.append(building_id)
            else:
                production_building_ids.append(building_id)
    # print(production_building_ids)
    # print(military_building_ids)
    # print(special_building_ids)

    description = ''
    if production_building_ids:
        description += '\u2028`Budynki Produkcyjne`\n'
        for building_id in production_building_ids:
            description = makeline(description, building_id)

    if military_building_ids:
        description += '\u2028\n`Budynki Wojskowe`\n'
        for building_id in military_building_ids:
            description = makeline(description, building_id)

    if special_building_ids:
        description += '\u2028\n`Budynki Specjalne`\n'
        for building_id in special_building_ids:
            description = makeline(description, building_id)

    connection.close()
    return description


def get_item_income_description(hunger_income: dict):
    def makeline(desc: str, item_id: int):
        pos_item_quantity, neg_item_quantity, name, emoji = hunger_income[item_id].values()
        print(hunger_income[item_id].values())
        print(pos_item_quantity)
        print(type(pos_item_quantity))
        print(neg_item_quantity)
        print(type(neg_item_quantity))

        item_quantity = pos_item_quantity + neg_item_quantity

        if item_quantity > 0:  # Assign an emoji indicator to income/cost
            desc += f'<:small_triangle_up:1260292468704809071> {emoji} `{round(item_quantity, 1)}` {name}\n'
        elif item_quantity == 0:
            desc += f':small_orange_diamond: {emoji} `{round(item_quantity, 1)}` {name}\n'
        else:
            desc += f'<:small_triangle_down:1260292467044122636> {emoji} `{round(item_quantity, 1)}` {name}\n'
        # desc += '\n'

        return desc

    description = ''
    for item_id in hunger_income:
        description = makeline(description, item_id)

    return description


# Build an army info table as tabulated strings and return them as a list of strings
# Input is a list of lists of required fields
# Also country_id for checking invisible units
async def build_army_info(query, country_id):
    table_list = []
    indexes = [7, 33, 52, 85, 97, 142, 187, 212, 232]
    template = list("""Armia: $                         $          
Jdnst: $                         Ruchy: $   
Typ:   $                                    
Kraj:  $                        Liczebność: 
Prwnc: $                        $           
Pchdz: $""")
    for unit in query:
        # |    7        |33 |        52       |   85  |      97     |    142   |   |  187       |    212    |   232    |
        # | Armia 1 | 1 | 1 | Wojownicy 1 | 1 | 1 | 1 | Templat | 1 | Karbadia | 1 | Test2 | 52 | 100 | 100 |Kanonia|50|
        aname, aid, vis, uname, uid, lmoves, moves, tname, tid, cname, cid, pname, pid, quan, astr, oname, oid = unit

        if not (country_id == 0 or country_id == cid) and vis == 0:
            pass
        elif (country_id == 0 or country_id == cid) and vis == 0:
            vis = "Niewidoczny"
        else:
            vis = "Widoczny"

        new_field = list("""Armia: $                         $          
Jdnst: $                         Ruchy: $   
Typ:   $                                    
Kraj:  $                        Liczebność: 
Prwnc: $                        $           
Pchdz: $""")

        word_list = [f"{aname} #{aid}", f"{vis}", f"{uname} #{uid}", f"{lmoves}/{moves}", f"{tname} #{tid}",
                     f"{cname}", f"{pname} #{pid}", f"{int(astr)}/{quan} {int((astr / quan) * 100)}%",
                     f"{oname} #{oid}"]

        for n, i in enumerate(indexes):
            new_field[indexes[n]: indexes[n] + len(word_list[n])] = list(word_list[n])

        table_list.append(''.join(new_field))
    return table_list


# /army list
async def build_army_list(country_id: int):
    connection = db.pax_engine.connect()
    table = connection.execute(text(
        f"""SELECT 
              a.army_name, 
              a.army_id, 
              a.army_unit_name, 
              a.army_unit_id, 
              ut.unit_name, 
              ut.unit_template_id, 
              uc.item_quantity, 
              a.army_strenght, 
              a.province_id, 
              a.army_movement_left, 
              ut.unit_movement 
            FROM 
              armies a 
              INNER JOIN units ut ON a.unit_template_id = ut.unit_template_id 
              INNER JOIN units_cost uc ON a.unit_template_id = uc.unit_template_id 
            WHERE 
              uc.item_id = 3 
              AND a.country_id = {country_id};
          """)).fetchall()

    df = pd.DataFrame(table, columns=[
        'aname', 'aid', 'uname', 'uid', 'utname', 'utid', 'qua', 'str', 'pid', 'aml', 'um'])
    df = df.sort_values(by=['aid', 'uid'])
    df2 = pd.DataFrame(columns=[
        'Armia (ID)', 'Jednostka (ID)', 'Typ Jednostki (ID)', 'Liczebność', 'Prwnc', 'Ruch'])
    for i, row in df.iterrows():
        army = f"{row.iloc[0]} ({row.iloc[1]})"
        unit = f"{row.iloc[2]} ({row.iloc[3]})"
        template = f"{row.iloc[4]} ({row.iloc[5]})"
        quantity = f"{int(row.iloc[6] / 100 * row.iloc[7])}/{row.iloc[6]} {row.iloc[7]}%"
        province = f"#{row.iloc[8]}"
        movement = f"{row.iloc[9]}/{row.iloc[10]}"
        df2.loc[f'{i}'] = [army, unit, template, quantity, province, movement]

    return df2


async def build_army_list_admin():
    connection = db.pax_engine.connect()
    table = connection.execute(text(
        f"""SELECT 
              a.army_name, 
              a.army_id, 
              a.army_unit_name, 
              a.army_unit_id, 
              ut.unit_name, 
              ut.unit_template_id, 
              uc.item_quantity, 
              a.army_strenght, 
              a.province_id, 
              a.army_movement_left, 
              ut.unit_movement 
            FROM 
              armies a 
              INNER JOIN units ut ON a.unit_template_id = ut.unit_template_id 
              INNER JOIN units_cost uc ON a.unit_template_id = uc.unit_template_id 
            WHERE 
              uc.item_id = 3;
          """)).fetchall()

    df = pd.DataFrame(table, columns=[
        'aname', 'aid', 'uname', 'uid', 'utname', 'utid', 'qua', 'str', 'pid', 'aml', 'um'])
    df = df.sort_values(by=['aid'])
    df2 = pd.DataFrame(columns=[
        'Armia (ID)', 'Jednostka (ID)', 'Typ Jednostki (ID)', 'Liczebność', 'Prwnc', 'Ruch'])
    for i, row in df.iterrows():
        army = f"{row.iloc[0]} ({row.iloc[1]})"
        unit = f"{row.iloc[2]} ({row.iloc[3]})"
        template = f"{row.iloc[4]} ({row.iloc[5]})"
        quantity = f"{int(row.iloc[6] / 100 * row.iloc[7])}/{row.iloc[6]} {row.iloc[7]}%"
        province = f"#{row.iloc[8]}"
        movement = f"{row.iloc[9]}/{row.iloc[10]}"
        df2.loc[f'{i}'] = [army, unit, template, quantity, province, movement]

    return df2


# /army order
async def build_army_order_move(country_id):
    move_orders = db.pax_engine.connect().execute(text(
        f'SELECT mo.order_id, a.army_name, a.army_id, a.army_unit_name, a.army_unit_id, '
        f'p1.province_name, p1.province_id, p2.province_name, p2.province_id, mo.datetime '
        f'FROM movement_orders mo NATURAL JOIN armies a '
        f'INNER JOIN provinces p1 ON mo.origin_province_id = p1.province_id '
        f'INNER JOIN provinces p2 ON mo.target_province_id = p2.province_id '
        f'WHERE a.country_id = {country_id[0]} '
        f'ORDER BY mo.datetime, mo.order_id, a.army_id, a.army_unit_id ')).fetchall()

    d = {}
    o = {}
    for x in move_orders:
        if x[2] not in d:
            d[x[2]] = []
            o[x[2]] = []
        if x[4] not in [t[4] for t in d[x[2]]]:
            d[x[2]].append(x)
        if x[0] not in [u[0] for u in o[x[2]]]:
            o[x[2]].append([x[0]] + list(x[5:10]))

    strings = []
    for x in d:
        s = '\u001b[1;37mJednostki:\u001b[0;0m\n'

        title = f"{d[x][0][1]} #{d[x][0][2]}"
        for y in d[x]:
            z = '   •' + f'{y[3].ljust(20)} #{y[4]}' + '\n'
            s = f"{s}{z}"
        s = s + '\n'
        for y in o[x]:
            z = f"\u001b[1;37mRozkaz #{str(y[0]).ljust(4)}{y[5]}\u001b[0;0m\n" \
                f"\u001b[0;31mZ : {y[1].ljust(20)} #{y[2]}\u001b[0;0m\n" \
                f"\u001b[0;32mDo: {y[3].ljust(20)} #{y[4]}\u001b[0;0m\n"
            s = f"{s}{z}"
            # \u001b[0;32m  \u001b[0;0m

        strings.append((title, s))
    embeds = []
    fields = []
    for x in strings:
        f = interactions.EmbedField(name=x[0], value=f"```ansi\n{x[1]}```", inline=False)
        if len(fields) > 20:
            embed = interactions.Embed(
                title=f"Rozkazy ruchu armii.",
                fields=fields)
            embeds.append(embed)
            fields = []
        fields.append(f)

    if fields:
        embed = interactions.Embed(
            title=f"Rozkazy ruchu armii.",
            fields=fields)
        embeds.append(embed)

    return embeds


# /province list
async def build_province_list(country_id: int):
    connection = db.pax_engine.connect()
    table = connection.execute(text(
        f"""
        SELECT 
  CONCAT(
    p.province_name, ' \u001b[0;30m(', 
    p.province_id, ')\u001b[0;0m'
  ), 
  r.region_name, 
  t.terrain_name, 
  it.item_name, 
  re.religion_name, 
  CONCAT(
    p.province_pops, 
    '(', 
    IFNULL(
      SUM(s.quantity * b.building_workers), 
      0
    ), 
    ')/', 
    pl.province_pops_limit
  ), 
  c.country_id, 
  cc.country_id 
FROM 
  provinces p NATURAL 
  JOIN regions r LEFT 
  JOIN items it ON p.good_id = it.item_id NATURAL 
  JOIN terrains t NATURAL 
  JOIN religions re 
  INNER JOIN countries c ON p.country_id = c.country_id 
  INNER JOIN countries cc ON p.controller_id = cc.country_id 
  LEFT JOIN structures s ON p.province_id = s.province_id 
  LEFT JOIN buildings b ON s.building_id = b.building_id 
  LEFT JOIN province_levels pl ON p.province_level = pl.province_level 
WHERE 
  p.country_id = {country_id} 
  OR p.controller_id = {country_id} 
GROUP BY 
  p.province_id 
ORDER BY 
  p.province_id;
        """
    )).fetchall()

    df = pd.DataFrame(table, columns=[
        'Prowincja (ID)', 'Region', 'Teren', 'Zasoby', 'Religia', 'Ludność', 'Status', 'Status2'])
    df['Status'] = df['Status'].astype(str)
    df['Status2'] = df['Status2'].astype(str)
    for i, row in df.iterrows():
        if df.at[i, 'Status'] == df.at[i, 'Status2']:
            df.at[i, 'Status'] = f"\u001b[0;32mKontrola\u001b[0;0m"
        elif df.at[i, 'Status2'] == str(country_id):
            df.at[i, 'Status'] = f"\u001b[0;33mOkupacja\u001b[0;0m"
        elif df.at[i, 'Status'] == str(country_id):
            df.at[i, 'Status'] = f"\u001b[0;31mOkupacja\u001b[0;0m"
    df.drop(['Status2'], axis=1, inplace=True)
    return df


async def build_province_list_admin():
    connection = db.pax_engine.connect()
    table = connection.execute(text(
        f"""
        SELECT 
  CONCAT(
    p.province_name, ' \u001b[0;30m(', 
    p.province_id, ')\u001b[0;0m'
  ), 
  r.region_name, 
  t.terrain_name, 
  it.item_name, 
  re.religion_name, 
  CONCAT(
    p.province_pops, 
    '(', 
    IFNULL(
      SUM(s.quantity * b.building_workers), 
      0
    ), 
    ')/', 
    pl.province_pops_limit
  ), 
  c.country_id, 
  cc.country_id 
FROM 
  provinces p NATURAL 
  JOIN regions r LEFT 
  JOIN items it ON p.good_id = it.item_id  NATURAL 
  JOIN terrains t NATURAL 
  JOIN religions re 
  INNER JOIN countries c ON p.country_id = c.country_id 
  INNER JOIN countries cc ON p.controller_id = cc.country_id 
  LEFT JOIN structures s ON p.province_id = s.province_id 
  LEFT JOIN buildings b ON s.building_id = b.building_id 
  LEFT JOIN province_levels pl ON p.province_level = pl.province_level 
WHERE 
  p.province_id BETWEEN 1 AND 251 
GROUP BY 
  p.province_id 
ORDER BY 
  p.province_id;
        """)).fetchall()

    df = pd.DataFrame(table, columns=[
        'Prowincja (ID)', 'Region', 'Teren', 'Zasoby', 'Religia', 'Ludność', 'Status', 'Status2'])
    for i, row in df.iterrows():
        if df.at[i, 'Status'] == 255:
            df.at[i, 'Status'] = f"\u001b[0;34mPuste\u001b[0;0m"
        elif df.at[i, 'Status'] == df.at[i, 'Status2']:
            df.at[i, 'Status'] = f"\u001b[0;32mKontrola\u001b[0;0m"
        else:
            df.at[i, 'Status'] = f"\u001b[0;31mOkupacja\u001b[0;0m"
    df.drop(['Status2'], axis=1, inplace=True)
    return df


async def build_province_embed(self, province_id: int, country_id: int, all_province_incomes: dict):
    embeds = []
    connection = db.pax_engine.connect()
    (province_id, province_name, region_name, terrain_name, terrain_image_url, religion_name, good_name,
     cid1, cn1, color, cid2, cn2, province_level, pop_limit, pop_income) = connection.execute(text(
        f'SELECT p.province_id, p.province_name, rg.region_name, t.terrain_name, t.terrain_image_url, '
        f'rl.religion_name, i.item_name, c.country_id, c.country_name, c.country_color, cc.country_id, cc.country_name, '
        f'p.province_level, pl.province_pops_limit, pl.province_pops_income '
        f'FROM provinces p NATURAL JOIN religions rl '
        f'NATURAL JOIN terrains t '
        f'LEFT JOIN items i ON p.good_id = i.item_id '
        f'NATURAL JOIN regions rg '
        f"INNER JOIN countries c ON p.country_id = c.country_id "
        f"INNER JOIN countries cc ON p.controller_id = cc.country_id "
        f"NATURAL JOIN province_levels pl "
        f'WHERE province_id = {province_id}'
    )).fetchone()
    if country_id == 0:
        country_id = cid1
    if not good_name:
        good_name = "-"
    pops = connection.execute(text(
        f'SELECT SUM(province_pops) FROM provinces WHERE province_id = "{province_id}"')).fetchone()[0]
    pops = float(pops) if pops is not None else 0
    workers_needed = connection.execute(text(
        f'SELECT SUM(building_workers * quantity) FROM provinces NATURAL JOIN structures NATURAL JOIN buildings '
        f'WHERE province_id = {province_id}')).fetchone()[0]
    workers_needed = float(workers_needed) if workers_needed is not None else 0
    conscripted = connection.execute(text(f"SELECT COUNT(*) FROM armies "
                                          f"LEFT JOIN provinces ON armies.province_id = provinces.province_id "
                                          f"WHERE armies.army_origin = {province_id} "
                                          f"AND armies.army_conscripted = 1")).fetchone()[0]
    conscripted = float(conscripted) if conscripted is not None else 0

    # Getting the predicted change of pops for the next round
    if all_province_incomes['hunger_incomes'][province_id].hunger < 0.8:  # Subtract pop_income
        if pops - pop_income < 0:  # Can't go below 0 pops
            pop_income = pops
        pop_change = f' 🔻{round(pop_income, 2)}/turę'
    elif all_province_incomes['hunger_incomes'][province_id].hunger >= 1:  # Add pop_income
        if pops + pop_income > pop_limit:  # Can't go above province cap
            pop_income = pop_limit - pops
        if pop_income <= 0:
            pop_change = f' 🔸0/turę'
        else:
            pop_change = f' ▲{round(pop_income, 2)}/turę'
    else:
        pop_change = f' 🔸0/turę'

    # Getting the workers percentage
    if workers_needed == 0:
        worker_percentage = ''
    else:
        worker_percentage = f' ({round(((pops - conscripted) / workers_needed) * 100, 1)}%)'

    # Coloring controller names
    if cid1 == country_id:
        cn1 = f"\u001b[0;32m{cn1}\u001b[0;0m"
    else:
        cn1 = f"\u001b[0;31m{cn1}\u001b[0;0m"
    if cid2 == country_id:
        cn2 = f"\u001b[0;32m{cn2}\u001b[0;0m"
    else:
        cn2 = f"\u001b[0;31m{cn2}\u001b[0;0m"

    # Creating fields
    pop_field = pd.DataFrame([['Mieszkańcy:', f'{pops}/{pop_limit}{pop_change}'],
                              ['Powołani:', f'{conscripted}'],
                              ['Pracownicy:', f'{pops - conscripted}/{workers_needed}{worker_percentage}']],
                             columns=['12345678901', '123456789012345678901234'])
    pop_field = pop_field.to_markdown(index=False).split("\n", maxsplit=2)[2]
    pop_field = re.sub('..\\n..', '\n', pop_field).replace(' |', ' ')

    status_field = pd.DataFrame([['Właściciel:', f'{cn1}'],
                                 ['Kontroler:', f'{cn2}']],
                                columns=['1234567890', '1234567890123456789012345'])
    status_field = status_field.to_markdown(index=False).split("\n", maxsplit=2)[2]
    status_field = re.sub('..\\n..', '\n', status_field).replace(' |', ' ')

    # Creating embed elements
    f0 = interactions.EmbedField(name=" ", value=" ", inline=False)
    f1 = interactions.EmbedField(name="Region", value=f"```{region_name}```", inline=True)
    f2 = interactions.EmbedField(name="Teren", value=f"```{terrain_name}```", inline=True)
    f3 = interactions.EmbedField(name="Religia", value=f"```{religion_name}```", inline=True)
    f4 = interactions.EmbedField(name="Zasoby", value=f"```{good_name}```", inline=True)
    f5 = interactions.EmbedField(name="Populacja", value=f"```{pop_field[2:-2]}```", inline=False)
    f6 = interactions.EmbedField(name="Status", value=f"```ansi\n{status_field[2:-2]}```", inline=False)

    fields = [f1, f2, f0, f3, f4, f5, f6]

    # Get economy info
    if 3 not in all_province_incomes['hunger_incomes'][province_id].buildings_incomes:  # If no food
        all_province_incomes['hunger_incomes'][province_id].buildings_incomes[3] = \
            {'neg_quantity': 0, 'pos_quantity': 0, 'name': 'Żywność', 'emoji': '<:Zywnosc:1259245985272561815>'}
    if 2 not in all_province_incomes['hunger_incomes'][province_id].buildings_incomes:  # If no gold income
        all_province_incomes['hunger_incomes'][province_id].buildings_incomes[2] = \
            {'neg_quantity': 0, 'pos_quantity': 0, 'name': 'Talary', 'emoji': '<:Talary:1259245998698659850>'}
    all_province_incomes['hunger_incomes'][province_id].buildings_incomes[3]['neg_quantity'] -= pops
    # Subtract eaten food
    all_province_incomes['hunger_incomes'][province_id].buildings_incomes[2]['pos_quantity'] += (pops
                                                                                                 * configure['POP_TAX'])
    # Add gold income from tax

    economy_description = get_item_income_description(
        all_province_incomes['hunger_incomes'][province_id].buildings_incomes)
    economy_lines = economy_description.split('\n')
    economy_field_title = 'Ekonomia'

    pages = pagify(economy_lines, max_char=1000)
    for page in pages:
        fields.append(interactions.EmbedField(name=economy_field_title, value=page, inline=False))
        economy_field_title = ''

    # Get buildings info
    # print(f'building: {province_incomes[province_id]}')
    if not all_province_incomes['province_incomes'][province_id].buildings_incomes:
        fields.append(interactions.EmbedField(name='Budynki', value='Brak.', inline=False))
    else:
        summed_province_income = sum_building_incomes(
            {province_id: all_province_incomes['province_incomes'][province_id]})
        building_description = get_buildings_income_description(summed_province_income.buildings_incomes)

        building_description = building_description[1:].split('\u2028')
        building_type_title = 'Budynki Produkcyjne'
        buildings_lines = {}
        for building_line in building_description:
            if 'Budynki' in building_line:
                building_type_title = building_line.strip()[1:-1]
                buildings_lines[building_type_title] = []
                continue
            buildings_lines[building_type_title].append(building_line)
        for building_type_title in buildings_lines:
            pages = pagify(buildings_lines[building_type_title], max_char=1000)
            for i, page in enumerate(pages):
                fields.append(interactions.EmbedField(name=building_type_title, value=page, inline=True))
                if i % 2 == 1:  # Add a blank inline=False field every second field to maintain two columns
                    fields.append(f0)
                building_type_title = ' '
                if i == 0:
                    building_type_title = '\u2800'

    embed_author = await country_author(self, cid1)
    image = interactions.EmbedAttachment(url=terrain_image_url)
    # Building the Embed

    embed = interactions.Embed(
        color=int(color, 16),
        title=f"{province_name} (#{province_id}), poziom {roman.toRoman(province_level)}",
        author=embed_author,
        # description=description,
        fields=fields,
        images=[image]
    )
    embeds.insert(0, embed)
    connection.close()
    return embeds


# /info country
async def build_country_embed(self, country_id: int):
    connection = db.pax_engine.connect()
    query = connection.execute(text(
        f"""
        SELECT 
          r.religion_id, 
          c.country_id, 
          p.player_id, 
          p.player_name, 
          p.player_rank, 
          c.country_name, 
          c.country_desc, 
          c.country_color, 
          c.country_ruler, 
          c.country_government, 
          c.country_capital, 
          c.country_bio_url, 
          c.country_image_url, 
          c.country_credo, 
          c.country_credo_image, 
          c.channel_id, 
          r.religion_name, 
          r.religion_head, 
          r.religion_capital, 
          r.religion_color, 
          r.religion_bio_url, 
          r.religion_image_url, 
          r.religion_credo, 
          r.religion_credo_image 
        FROM 
          players p NATURAL 
          JOIN countries c NATURAL 
          JOIN religions r 
        WHERE 
          country_id = "{country_id}"
        """
    )).fetchall()
    # Repairing names for multiple players on one country
    owners = ''
    for x in query:
        member = await self.bot.fetch_member(user_id=x[2], guild_id=configure['GUILD'])
        user = member.user
        owners = f"{user.tag} {owners}"
    query = list(query[0])
    query[3] = owners
    query2 = connection.execute(text(
        f'SELECT SUM(province_pops), COUNT(*) FROM provinces WHERE country_id = "{country_id}"')).fetchone()
    query3 = connection.execute(text(
        f'SELECT province_name FROM provinces WHERE province_id = "{query[10]}"')).fetchone()
    query4 = connection.execute(text(
        f'SELECT COUNT(*) FROM countries WHERE NOT country_id BETWEEN 253 AND 255')).fetchone()
    member = await self.bot.fetch_member(user_id=query[2], guild_id=configure['GUILD'])
    user = member.user
    # Creating embed elements
    embed_footer = interactions.EmbedFooter(
        text=query[13],
        icon_url=query[14]
    )
    if (query[13] is None) or (query[14] is None):
        embed_footer = None
    embed_thumbnail = interactions.EmbedAttachment(
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
    f4 = interactions.EmbedField(name="Domena", value=f"```{query2[1]} prowincji```", inline=True)
    f5 = interactions.EmbedField(name="Religia", value=f"```{query[16]}```", inline=True)
    f6 = interactions.EmbedField(name="Populacja", value=f"```{query2[0]} osób```", inline=True)
    f7 = interactions.EmbedField(name="Dyplomacja", value=f"{query[15]}", inline=True)
    f8 = interactions.EmbedField(name="ID Kraju", value=f"{country_id} / {query4[0]}", inline=True)

    # Building the Embed
    embed = interactions.Embed(
        color=int(query[7], 16),
        title=query[5],
        footer=embed_footer,
        url=query[11],
        thumbnail=embed_thumbnail,
        author=embed_author,
        fields=[f1, f2, fb, f3, f4, fb, f5, f6, fb, f7, f8]
    )
    connection.close()
    return embed


# /inventory items
async def build_item_embed_good(ctx, self, item_id: int, country_id: int, item_query: list):
    province_query = db.pax_engine.connect().execute(text(
        f'SELECT item_id, item_name, item_color, item_image_url, item_desc, quantity, item_type '
        f'FROM items NATURAL JOIN inventories '
        f'WHERE item_id = "{item_id}" AND country_id = "{country_id}"'
    )).fetchone()
    # Creating embed elements
    user = ctx.author
    embed_thumbnail = interactions.EmbedAttachment(
        url=item_query[3]
    )
    embed_author = interactions.EmbedAuthor(
        name=user.tag,
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
        thumbnail=embed_thumbnail,
        author=embed_author,
        fields=[f1, f2, f3, f4]
    )
    return embed


async def build_item_embed_talar(ctx, self):
    user = ctx.author
    embed_thumbnail = interactions.EmbedAttachment(
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
                                                                                  "https://i.imgur.com/yV4QfJM.png",
            "https://i.imgur.com/Rr7Ko4w.png", "https://i.imgur.com/L2DNU9a.png")
    embed.set_image(url=random.choice(meme))
    return embed


async def build_item_embed_talary(ctx, self, item_id: int, country_id: int, item_query: list):
    province_query = db.pax_engine.connect().execute(text(
        f'SELECT item_id, item_name, item_color, item_image_url, item_desc, quantity, item_type '
        f'FROM items NATURAL JOIN inventories '
        f'WHERE item_id = "{item_id}" AND country_id = "{country_id}"'
    )).fetchone()
    user = ctx.author
    embed_thumbnail = interactions.EmbedAttachment(
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
    # Get all info from database
    item_query = db.pax_engine.connect().execute(text(
        f'SELECT item_id, item_name, item_color, item_image_url, item_desc, quantity, item_type '
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
    return embed


async def build_item_embed_admin(item_id: int):
    connection = db.pax_engine.connect()
    query = connection.execute(text(
        f'SELECT * FROM items WHERE item_id = "{item_id}"'
    )).fetchall()
    query = list(query[0])
    # Creating embed elements
    embed_thumbnail = interactions.EmbedAttachment(
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
fb = interactions.EmbedField(name=" ", value=" ", inline=False)


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
                                       f"\nNiszczenie budynków.```", inline=True)
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
def ic_commands():
    f1 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/commands\u001b[0;0m```"
                                       f"Wyświetla ściągę komend.", inline=False)
    embed = interactions.Embed(
        title="/commands",
        description="Wyświetla ściągę wszystkich komend na serwerze Pax Zeonica.",
        author=author,
        fields=[f1]
    )
    return embed


def ic_info_command():
    f1 = interactions.EmbedField(name="[nazwa_komendy]", value=f"```ansi"
                                                         f"\n\u001b[0;31m•Nazwa Komendy\u001b[0;0m"
                                                         f"\nWyświetla informacje danej komendy.```", inline=True)
    f2 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/info command [/info command]\u001b[0;0m```"
                                       f"Wyświetla stronę na której się właśnie znajdujesz.", inline=False)
    embed = interactions.Embed(
        title="/info command [nazwa_komendy]",
        description="Wyświetla dokładne informacje dotyczące danej komendy.\n"
                    "Właśnie jej używasz żeby sprawdzić informacje o komendzie '/info command'.",
        author=author,
        fields=[f1, f2]
    )
    return embed


def ic_info_country():
    f1 = interactions.EmbedField(name="(kraj)", value=f"```ansi"
                                                      f"\n\u001b[0;31m•@ gracza\u001b[0;0m"
                                                      f"\nWyświetla informacje o kraju danego gracza."
                                                      f"\n\u001b[0;31m•Nazwa Kraju\u001b[0;0m"
                                                      f"\nWyświetla informacje o danym kraju.```", inline=True)
    f2 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/info country (@XnraD)\u001b[0;0m```"
                                       f"Wyświetla informacje o kraju XnraD'a (Karbadia)."
                                       f"```ansi\n\u001b[0;40m/info country (Karbadia)\u001b[0;0m```"
                                       f"Wyświetla informacje o kraju Karbadia.", inline=False)
    embed = interactions.Embed(
        title="/info country (kraj)",
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
                                                      f"\n\u001b[0;31m•Terenów\u001b[0;0m"
                                                      f"\n11 typów terenów."
                                                      f"\n\u001b[0;31m•Zasobów\u001b[0;0m"
                                                      f"\n30 różnych typów zasobów."
                                                      f"\n\u001b[0;31m•Polityczna\u001b[0;0m"
                                                      f"\nWasze świetne państwa."
                                                      f"\n\u001b[0;31m•Religii\u001b[0;0m"
                                                      f"\nReligie wasze i nasze."
                                                      f"\n\u001b[0;31m•Populacji\u001b[0;0m"
                                                      f"\nPopulacje prowincji."
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
    f5 = interactions.EmbedField(name="Przykłady: ",
                                 value=f"```ansi\n\u001b[0;40m/mapa [Polityczna] [Nie] [Armie]\u001b[0;0m```"
                                       f"Generuje mapę z państwami graczy i armiami."
                                       f"```ansi\n\u001b[0;40m/mapa [Prowincji] [Tak] [ID Prowincji]\u001b[0;0m```"
                                       f"Generuje mapę prowincji, konturami i ID prowincji.", inline=False)

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
                                       f"Wyświela ekwipunek w postaci stron."
                                       f"```ansi\n\u001b[0;40m/inventory list [Prosty]\u001b[0;0m```"
                                       f"Wyświela ekwipunek w postaci listy.", inline=False)
    embed = interactions.Embed(
        title="/inventory list [tryb] {admin}",
        description="Wyświetla ilość itemów które posiada państwo gracza oraz ich balans.\n"
                    "W trybie dokładnym wyświetla również więcej informacji, np. szczegóły wydatków.",
        author=author,
        fields=[f1, f2, f3]
    )
    return embed


def ic_inventory_item():
    f1 = interactions.EmbedField(name="[item]", value=f"```ansi"
                                                      f"\n\u001b[0;31m•Nazwa Itemu\u001b[0;0m"
                                                      f"\nWyświetla dany item.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi"
                                                       f"\n\u001b[0;35m•admin\u001b[0;0m"
                                                       f"\nPokazuje wszystkie możliwe informacje."
                                                       f"\n\u001b[0;35m•@ gracza\u001b[0;0m"
                                                       f"\nWyświetla itemy kraju danego gracza."
                                                       f"\n\u001b[0;35m•Nazwa Kraju\u001b[0;0m"
                                                       f"\nWyświetla itemy danego kraju.```", inline=True)
    f3 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/inventory item [Talary]\u001b[0;0m```"
                                       f"Wyświetla informacje o talarach w kraju.", inline=False)
    embed = interactions.Embed(
        title="/inventory item [item] {admin}",
        description="Wyświetla informacje o itemach.",
        author=author,
        fields=[f1, f2, f3]
    )
    return embed


def ic_inventory_give():
    f1 = interactions.EmbedField(name="[kraj]", value=f"```ansi"
                                                      f"\n\u001b[0;31m•@ gracza\u001b[0;0m"
                                                      f"\nGracz do którego kraju chcemy dać itemy."
                                                      f"\n\u001b[0;31m•Nazwa Kraju\u001b[0;0m"
                                                      f"\nKraj do którego chcemy dać itemy.```", inline=True)
    f2 = interactions.EmbedField(name="[argument]", value=f"```ansi"
                                                          f"\n\u001b[0;32m•Ilość & Item\u001b[0;0m"
                                                          f"\nRodzaj i ilość itemów które chcemy dać.```", inline=True)
    f3 = interactions.EmbedField(name="{admin}", value=f"```ansi"
                                                       f"\n\u001b[0;35m•True\u001b[0;0m"
                                                       f"\nPozwala na spawnowanie itemów.```", inline=True)
    f4 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/inventory give [@XnraD] [10 Talary]\u001b[0;0m```"
                                       f"Daje państwu XnraD'a (Karbadia) 10 talarów."
                                       f"```ansi\n\u001b[0;40m/inventory give [Karbadia] [15 Drewno,"
                                       f" 20 Kamień]\u001b[0;0m```"
                                       f"Daje państwu Karbadia 15 drewna i 20 kamienia.", inline=False)
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
                                       f"Wyświela armie w postaci stron."
                                       f"```ansi\n\u001b[0;40m/army list [Prosty]\u001b[0;0m```"
                                       f"Wyświela armie w postaci listy.", inline=False)
    embed = interactions.Embed(
        title="/army list [tryb] {admin}",
        description="Wyświetla powołane armie które posiada państwo gracza.\n"
                    "W trybie dokładnym wyświetla również więcej informacji, np. pochodzenie jednostki.",
        author=author,
        fields=[f1, f2, f3]
    )
    return embed


def ic_army_templates():
    f1 = interactions.EmbedField(name="(jednostka)", value=f"```ansi"
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
                                 value=f"```ansi\n\u001b[0;40m/army templates (Wojownicy)\u001b[0;0m```"
                                       f"Wyświela informacje o szablonie jednostki 'Wojownicy'."
                                       f"```ansi\n\u001b[0;40m/building templates (Tartak)\u001b[0;0m```"
                                       f"Wyświela informacje o szablonie budynku 'Tartak'.", inline=False)
    embed = interactions.Embed(
        title="/army templates (jednostka) {admin}",
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
                                                           f"\n\u001b[0;32m•Szablon jednostki zawodowej\u001b[0;0m"
                                                           f"\nTaka jednostka zostanie zrekrutowana.```", inline=True)
    f3 = interactions.EmbedField(name="(nazwa_jednostki)", value=f"```ansi"
                                                                 f"\n\u001b[0;33m•Nazwa jednostki\u001b[0;0m"
                                                                 f"\nNazwa nowo utworzonej jednostki.```", inline=True)
    f4 = interactions.EmbedField(name="(nazwa_armii)", value=f"```ansi"
                                                             f"\n\u001b[0;34m•Nazwa armii\u001b[0;0m"
                                                             f"\nNazwa nowo utworzonej armii.```", inline=True)
    f5 = interactions.EmbedField(name="{admin}", value=f"```ansi"
                                                       f"\n\u001b[0;35m•@ gracza\u001b[0;0m"
                                                       f"\nSpawnuje jednostkę krajowi danego gracza."
                                                       f"\n\u001b[0;35m•Nazwa kraju\u001b[0;0m"
                                                       f"\nSpawnuje jednostkę danemu krajowi.```", inline=True)
    f6 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/army recruit [#53] [Wojownicy]\u001b[0;0m```"
                                       f"Rekrutuje w prowincji #53 jednostkę Wojowników i nadaje im automatycznie"
                                       f"wygenerowaną nazwę jednostki oraz armii."
                                       f"\nOdejmuje potrzebną ilość populacji z prowincji #53."
                                       f"\nOdejmuje potrzebną ilość pozostałych itemów z inventory."
                                       f"```ansi\n\u001b[0;40m/army recruit [#53] [Wojownicy] (Gwardia Królewska) "
                                       f"(Pierwsza Chorągiew)\u001b[0;0m```"
                                       f"To samo co wyżej, ale na dodatek ustawia nazwę jednostki oraz nazwę armii co"
                                       f" ułatwia jej przyszłe zarządzanie i dodaje nam rigczu na polu bitwy.",
                                 inline=False)
    embed = interactions.Embed(
        title="/army recruit [prowincja] [jednostka] (nazwa_jednostki) (nazwa_armii) {admin}",
        description="Rekrutuje daną jednostkę wojska zawodowego w danej prowincji.\n"
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
                                       f"Rozwiązuje całą armię."
                                       f"\nZwraca część kosztów rekrutacyjnych oraz żywych żołnierzy do "
                                       f"prowincji ich pochodzenia."
                                       f"```ansi\n\u001b[0;40m/army disband [Jednostka] [#12, #13]\u001b[0;0m```"
                                       f"To samo co wyżej, ale kilka jednostek na raz i po ID.",
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
                                 value=f"```ansi\n\u001b[0;40m/army reorg [#53]\u001b[0;0m```"
                                       f"Wyświela informacje o organizacji armii w prowincji #53."
                                       "```ansi\n\u001b[0;40m/army reorg [#53] ({#1: +#13, +#12})\u001b[0;0m```"
                                       f"Przenosi jednostki o #13 i #12 do armii #1."
                                       "```ansi\n\u001b[0;40m/army reorg [#53] ({+: +#13, +#12})\u001b[0;0m```"
                                       f"Tworzy nową armię o kolejnym wolnym ID i dodaje do niej jednostki #13 i #12."
                                       "```ansi\n\u001b[0;40m/army reorg [#53] ({#1: -#13}, {#3; +#12})\u001b[0;0m```"
                                       f"Usuwa jednostkę #13 z armii #1 i tworzy dla niej nową armię o kolejnym "
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
                                       f"Przywraca jednostkę 'Gwardia Królewska' do pełni sił."
                                       f"\nGdyby przedtem miała tylko 75% stanu osobowego z powodu bitew lub innych "
                                       f"powodów, teraz wróciła by do 100% sił."
                                       f"Odejęte zostanie również 25% bazowego kosztu jednostki z inventory kraju."
                                       f"```ansi\n\u001b[0;40m/army resupply [Armia] [#1, #2]\u001b[0;0m```"
                                       f"To samo co wyżej, ale kilka armii na raz.",
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
                                       f"Zmienia nazwę armii 'Pierwsza Chorągiew' na 'Chorągiew Cara'."
                                       f"```ansi\n\u001b[0;40m/army rename [Jednostka] [#13] "
                                       f"[Gwardia Cara] \u001b[0;0m```"
                                       f"Zmienia nazwę jednostki #13 na 'Gwardia Cara'.",
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
    f1 = interactions.EmbedField(name="[armia]", value=f"```ansi"
                                                       f"\n\u001b[0;31m•# armii\u001b[0;0m"
                                                       f"\nRusza armię o danym ID."
                                                       f"\n\u001b[0;31m•Nazwa armii\u001b[0;0m"
                                                       f"\nRusza armię o danej nazwie.```", inline=True)
    f2 = interactions.EmbedField(name="[granica]", value=f"```ansi"
                                                         f"\n\u001b[0;32m•# graniczącej prowincji\u001b[0;0m"
                                                         f"\nRusza do prowincji o danym ID."
                                                         f"\n\u001b[0;32m•Nazwa graniczącej prowincji\u001b[0;0m"
                                                         f"\nRusza do prowincji o danej nazwie.```", inline=True)
    f3 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\u001b[0;35m•admin\u001b[0;0m"
                                                       f"\nTeleportuje armię.```", inline=True)
    f4 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/army move [#1] [#50]\u001b[0;0m```"
                                       f"Dodaje rozkaz ruchu dla armii o ID #1 z graniczącej prowincji do "
                                       f"prowincji o ID #50."
                                       f"```ansi\n\u001b[0;40m/army move [Pierwsza Chorągiew] "
                                       f"[Kanonia]\u001b[0;0m```"
                                       f"Dodaje rozkaz ruchu dla armii o nazwie 'Pierwsza Chorągiew' z graniczącej "
                                       f"prowincji do prowincji o nazwie 'Kanonia'.", inline=False)
    embed = interactions.Embed(
        title="/army move [armia] [granica] {admin}",
        description="Rusza daną jednostkę na sąsiednią prowincję.",
        author=author,
        fields=[f1, f2, f3, f4]
    )
    return embed


def ic_army_orders():
    f1 = interactions.EmbedField(name="[typ]", value=f"```ansi"
                                                     f"\n\u001b[0;31m•recruit\u001b[0;0m"
                                                     f"\nWyświetla rozkazy rekrutacji armii."
                                                     f"\n\u001b[0;31m•reinforce\u001b[0;0m"
                                                     f"\nWyświetla rozkazy uzupełniania armii."
                                                     f"\n\u001b[0;31m•move\u001b[0;0m"
                                                     f"\nWyświetla rozkazy ruchu armii.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\n\u001b[0;35m•@ gracza\u001b[0;0m"
                                                       f"\nWyświetla budynki kraju danego gracza."
                                                       f"\n\u001b[0;35m•Nazwa Kraju\u001b[0;0m"
                                                       f"\nWyświetla budynki danego kraju.```", inline=True)
    f3 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/army orders [move]\u001b[0;0m```"
                                       f"Wyświetla rozkazy ruchu armii w formie listy.", inline=False)
    embed = interactions.Embed(
        title="/army orders [typ] {admin}",
        description="Wyświetla informacje o rozkazach.",
        author=author,
        fields=[f1, f2, f3]
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
                                       f"Wyświela budynki w postaci stron."
                                       f"```ansi\n\u001b[0;40m/building list [Prosty]\u001b[0;0m```"
                                       f"Wyświela budynki w postaci listy.", inline=False)
    embed = interactions.Embed(
        title="/building list [tryb] {admin}",
        description="Wyświetla zbudowane budynki które posiada państwo gracza.\n"
                    "W trybie dokładnym wyświetla również więcej informacji, np. opisy budynków.",
        author=author,
        fields=[f1, f2, f3]
    )
    return embed


def ic_building_templates():
    f1 = interactions.EmbedField(name="(budynek)", value=f"```ansi"
                                                         f"\n\u001b[0;31m•Dokładny\u001b[0;0m"
                                                         f"\nInformacje w postaci szczegółowych stron."
                                                         f"\n\u001b[0;31m•Prosty\u001b[0;0m"
                                                         f"\nInformacje w postaci prostej listy.```", inline=True)
    f2 = interactions.EmbedField(name="{admin}", value=f"```ansi\n"
                                                       f"\n\u001b[0;35m•admin\u001b[0;0m"
                                                       f"\nWyświetla wszystkie szablony budynków."
                                                       f"\n\u001b[0;35m•@ gracza\u001b[0;0m"
                                                       f"\nWyświetla szablony budynków kraju danego gracza."
                                                       f"\n\u001b[0;35m•Nazwa Kraju\u001b[0;0m"
                                                       f"\nWyświetla szablony budynków danego kraju.```", inline=True)
    f3 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/building templates [Dokładny]\u001b[0;0m```"
                                       f"Wyświela szablony budynków w postaci stron."
                                       f"```ansi\n\u001b[0;40m/building templates [Prosty]\u001b[0;0m```"
                                       f"Wyświela szablony budynków w postaci listy.", inline=False)
    embed = interactions.Embed(
        title="/building templates (budynek) {admin}",
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
                                                       f"\n\u001b[0;35m•True\u001b[0;0m"
                                                       f"\nPozwala na spawnowanie budynków```", inline=True)
    f4 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/building build [#53] [Tartak]\u001b[0;0m```"
                                       f"Buduje w prowincji #50 1 Tartak."
                                       f"\nW prowincji #53 zaczyna pracować dana ilość populacji."
                                       f"\nOdejmuje potrzebną ilość pozostałych itemów z inventory."
                                       f"```ansi\n\u001b[0;40m/building build [Kanonia] "
                                       f"[1 Tartak, 2 Kopalnia]\u001b[0;0m```"
                                       f"Buduje w prowincji Kanonia 1 Tartak i 2 Kopalnie.",
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
                                                         f"\n\u001b[0;31m•Szablon budynku\u001b[0;0m"
                                                         f"\nNiszczy taki budynek w danej prowincji.```",
                                 inline=True)
    f2 = interactions.EmbedField(name="[prowincja]", value=f"```ansi"
                                                           f"\n\u001b[0;31m•# prowincji\u001b[0;0m"
                                                           f"\nW prowincji o tym ID będzie zniszczony budynek."
                                                           f"\n\u001b[0;31m•Nazwa prowincji\u001b[0;0m"
                                                           f"\nW prowincji o tej nazwie będzie zniszczony budynek.```",
                                 inline=False)
    f3 = interactions.EmbedField(name="{admin}", value=f"```ansi"
                                                       f"\n\u001b[0;35m•True\u001b[0;0m"
                                                       f"\nPozwala na kasowanie budynków```", inline=True)
    f4 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/building destroy [#50] [Tartak]\u001b[0;0m```"
                                       f"Niszczy w prowincji #50 1 Tartak."
                                       f"\nPopulacja pracująca w tym budynku zostaje zwolniona."
                                       f"\nZwraca połowę kosztów w postaci surowców."
                                       f"```ansi\n\u001b[0;40m/building build [Kanonia] "
                                       f"[1 Tartak, 2 Kopalnia]\u001b[0;0m```"
                                       f"To samo co wyżej, ale kilka budynków na raz.",
                                 inline=False)
    embed = interactions.Embed(
        title="/building destroy [budynek] {admin}",
        description="Niszczy dany budynek zwracając część surowców do inventory oraz zwalniając robotników.\n"
                    "Możesz zniszczyć tylko budynki które posiadasz oraz kontrolujesz.",
        author=author,
        fields=[f1, f3, f2, f4]
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
                                       f"Wyświela prowincje w postaci stron."
                                       f"```ansi\n\u001b[0;40m/province list [Prosty]\u001b[0;0m```"
                                       f"Wyświela prowincje w postaci listy.", inline=False)
    embed = interactions.Embed(
        title="/province list [tryb] {admin}",
        description="Wyświetla prowincje które posiada kraj.\n"
                    "W trybie dokładnym wyświetla również więcej informacji, np. tamtejsze budynki i armie.",
        author=author,
        fields=[f1, f2, f3]
    )
    return embed


def ic_province_rename():
    f1 = interactions.EmbedField(name="[nazwa]", value=f"```ansi"
                                                       f"\n\u001b[0;31m•# prowincji\u001b[0;0m"
                                                       f"\nZmienia nazwę prowincji o danym ID."
                                                       f"\n\u001b[0;31m•Nazwa prowincji\u001b[0;0m"
                                                       f"\nZmienia nazwę prowincji o danej nazwie.```",
                                 inline=True)
    f2 = interactions.EmbedField(name="[nowa_nazwa]", value=f"```ansi"
                                                            f"\n\u001b[0;32m•Nowa nazwa\u001b[0;0m"
                                                            f"\nNadaje nową nazwę prowincji.```",
                                 inline=True)
    f3 = interactions.EmbedField(name="Przykłady:",
                                 value=f"```ansi\n\u001b[0;40m/province rename [Kanonia] [Skalla] \u001b[0;0m```"
                                       f"Zmienia nazwę prowincji 'Kanonia' na 'Skalla'."
                                       f"```ansi\n\u001b[0;40m/province rename [#53] [Skalla] \u001b[0;0m```"
                                       f"Zmienia nazwę prowincji #53 na 'Skalla'.",
                                 inline=False)
    embed = interactions.Embed(
        title="/province rename [nazwa] [nowa_nazwa]",
        description="Zmienia nazwę prowincji którą gracz posiada i kontroluje.\n"
                    "Pozwala na łatwiejsze zarządzanie prowincjami.",
        author=author,
        fields=[f1, f2, fb, f3]
    )
    return embed


async def b_building_templates(self, country_id):
    connection = db.pax_engine.connect()

    def makeline(building_mess: str, build_id: int):
        can_build = True

        building_costs = buildings_costs.loc[(buildings_costs['building_id'] == build_id) &
                                             (buildings_costs['country_id'] == country_id)].values.tolist()
        # ['building_id', 'country_id', 'building_emoji', 'building_name',
        #  'item_emoji', 'item_name', 'cost_quantity', 'inv_quantity']
        if not building_costs:
            return [interactions.Embed(title=f"GM zapomniał dodać koszt budynku! ID: {build_id}")]
        building_emoji, building_name = building_costs[0][2], building_costs[0][3]
        building_line = f'{building_emoji} **{building_name}** - Koszt: '

        for building_cost in building_costs:
            item_emoji, item_name, cost, inventory = building_cost[4], building_cost[5], building_cost[6], \
                building_cost[7]
            inventory = inventory if inventory is not None else 0
            if cost > inventory:  # Not enough items
                can_build = False
                building_line = building_line + f'{item_emoji} {item_name} [{inventory}/{cost}], '
            else:
                building_line = building_line + f'{item_emoji} **{item_name} [{inventory}/{cost}]**, '
        building_line = building_line[:-1]
        if can_build:
            building_line = ":small_blue_diamond:" + building_line
        else:
            building_line = ":black_medium_small_square:" + building_line
        building_mess = building_mess + building_line[:-1] + '\n'

        return building_mess

    building_message = ''
    if country_id == '%':  # If admin
        q = connection.execute(
            text(f'''
                SELECT 
                  building_id
                FROM 
                  country_buildings 
                WHERE
                  country_id LIKE '{country_id}';
                ''')).fetchall()
        country_id = 1
    else:
        q = connection.execute(
            text(f'''
                SELECT 
                  building_id
                FROM 
                  country_buildings 
                WHERE
                  country_id IN (255, {country_id})
                ORDER BY
                  building_id
                ''')).fetchall()
    building_ids = [x for xs in q for x in xs]

    # Get all costs
    q = connection.execute(
        text(f'''
SELECT 
  b.building_id, 
  inv.country_id, 
  b.building_emoji, 
  b.building_name, 
  it.item_emoji, 
  it.item_name, 
  bc.item_quantity, 
  inv.quantity 
FROM 
  country_buildings cb NATURAL 
  JOIN buildings b NATURAL 
  JOIN buildings_cost bc NATURAL 
  JOIN items it 
  LEFT JOIN inventories inv ON it.item_id = inv.item_id;
                    ''')).fetchall()
    # +-------------+------------+-------------------------------+---------------+-------------------------------+
    # | building_id | country_id | building_emoji                | building_name | item_emoji                    |
    # +-------------+------------+-------------------------------+---------------+-------------------------------+
    # |           1 |          1 | <:Tartak:1259978101442740327> | Tartak        | <:Talary:1259245998698659850> |
    # |           1 |          2 | <:Tartak:1259978101442740327> | Tartak        | <:Talary:1259245998698659850> |
    # |           1 |        253 | <:Tartak:1259978101442740327> | Tartak        | <:Talary:1259245998698659850> |
    # -----------+---------------+----------+
    #  item_name | item_quantity | quantity |
    # -----------+---------------+----------+
    #  Talary    |           150 |     1.00 |
    #  Talary    |           150 |     0.00 |
    #  Talary    |           150 |     0.00 |
    buildings_costs = pd.DataFrame(q, columns=['building_id', 'country_id', 'building_emoji', 'building_name',
                                               'item_emoji', 'item_name', 'cost_quantity', 'inv_quantity'])

    for building_id in building_ids:
        building_message = makeline(building_message, building_id)

    pages = pagify(dataframe=building_message[:-1].split('\n'), max_char=3900)

    country_color = connection.execute(
        text(f'''
                SELECT 
                  country_color
                FROM 
                  countries 
                WHERE
                  country_id = {country_id};
                ''')).fetchone()[0]  # 'FFFFFF'

    author = await country_author(self, country_id=country_id)
    footer = interactions.EmbedFooter(text=
                                      f"/building build [#53] [Tartak] | "
                                      f"/building build [Kanonia] [1 Tartak, 2 Kopalnia]")

    embeds = []
    for page in pages:
        embeds.append(interactions.Embed(
            title="Twoje szablony budynków",
            description=page,
            author=author,
            footer=footer,
            color=int(country_color, 16)
        ))
    return embeds


async def b_building_list(self, country_id):
    connection = db.pax_engine.connect()

    country_color = connection.execute(
        text(f'''
                    SELECT 
                      country_color
                    FROM 
                      countries 
                    WHERE
                      country_id = {country_id};
                    ''')).fetchone()[0]

    q = connection.execute(
        text(f'''
            SELECT 
              province_id
            FROM
              provinces
            WHERE
              country_id = {country_id}
              AND controller_id = {country_id}
            ''')).fetchall()
    province_ids = [x for xs in q for x in xs]

    incomes = {}
    # print(province_ids)
    incomes = get_provinces_incomes()

    province_incomes = {}
    for province_id in province_ids:
        province_incomes[province_id] = incomes[province_id]

    buildings = sum_building_incomes(province_incomes).buildings_incomes

    author = await country_author(self, country_id=country_id)
    footer = interactions.EmbedFooter(text=
                                      f"/building destroy [#27, #37] | "
                                      f"/building build [Kanonia] [1 Tartak, 2 Kopalnia]")

    description = get_buildings_income_description(buildings).split('\n')
    bits = pagify(description, 3900)

    embeds = []
    for bit in bits:
        embeds.append(interactions.Embed(
            title="Lista budynków",
            description=bit,
            author=author,
            footer=footer,
            color=int(country_color, 16)
        ))
    return embeds


async def b_inventory_list(self, country_id):
    def makeline(building_mess: str, item: list):
        item_id, quantity, item_name, item_desc, item_emoji = item
        if item_id not in country_income.buildings_incomes:
            pos_quantity, neg_quantity = 0, 0
        else:
            pos_quantity = country_income.buildings_incomes[item_id]['pos_quantity']
            neg_quantity = country_income.buildings_incomes[item_id]['neg_quantity']
            neg_quantity = abs(neg_quantity)
        balance = pos_quantity - neg_quantity
        if (quantity == 0) & (balance == 0):
            return building_mess

        line = f'{item_emoji} **{item_name} x{quantity}**'

        if (pos_quantity == 0) & (neg_quantity == 0):
            return building_mess + line + '\n'

        if balance > 0:  # Assign an emoji indicator to income/cost
            line += f' <:small_triangle_up:1260292468704809071> `{round(balance, 1)} (+{pos_quantity}/-{neg_quantity})`'
        elif balance == 0:
            line += f' :small_orange_diamond: `{round(balance, 1)} (+{pos_quantity}/-{neg_quantity})`'
        else:
            line += (f' <:small_triangle_down:1260292467044122636> '
                              f'`{round(balance, 1)} (+{pos_quantity}/-{neg_quantity})`')
            if quantity < abs(balance):
                line += f' :exclamation: __*{round(quantity / balance)}% popytu*__'

        return building_mess + line + '\n'

    connection = db.pax_engine.connect()

    # Get the country inventory
    inventory = connection.execute(
        text(f'''
            SELECT 
              inv.item_id, inv.quantity, i.item_name, i.item_desc, i.item_emoji 
            FROM 
              inventories inv NATURAL
              JOIN items i 
            WHERE 
              country_id={country_id}
            ORDER BY
              i.item_type
            ''')).fetchall()
    # +---------+----------+-----------+-----------------------+------------------------------------------+
    # | item_id | quantity | item_name | item_desc             | item_emoji                               |
    # +---------+----------+-----------+-----------------------+------------------------------------------+
    # |       1 |     1.00 | Talar     | Niezły z niego gość   | <:Talar:1259251488585416765>             |
    # |       2 |     1.00 | Talary    | Uniwersalna waluta, w | <:Talary:1259245998698659850>            |
    # |       3 |     0.00 | Żywność   | Zaopatrzenie złożone z| <:Zywnosc:1259245985272561815>           |

    # Get all incomes
    provinces_incomes = get_provinces_incomes()
    country_provinces = {}
    for province_id in provinces_incomes:
        if provinces_incomes[province_id].controller_id == country_id:
            country_provinces[province_id] = provinces_incomes[province_id]
    country_income = sum_item_incomes(country_provinces)
    print(country_income.buildings_incomes)
    if 3 not in country_income.buildings_incomes:
        country_income.buildings_incomes[3] = \
            {'neg_quantity': 0, 'pos_quantity': 0, 'name': 'Żywność', 'emoji': '<:Zywnosc:1259245985272561815>'}
    if 2 not in country_income.buildings_incomes:
        country_income.buildings_incomes[2] = \
            {'neg_quantity': 0, 'pos_quantity': 0, 'name': 'Talary', 'emoji': '<:Talary:1259245998698659850>'}
    country_income.buildings_incomes[3]['neg_quantity'] -= country_income.pops
    country_income.buildings_incomes[2]['pos_quantity'] += round(country_income.pops * configure['POP_TAX'], 1)

    item_message = ''
    for item in inventory:
        item_message = makeline(item_message, item)

    pages = pagify(dataframe=item_message[:-1].split('\n'), max_char=3900)

    country_color = connection.execute(
        text(f'''
                SELECT 
                  country_color
                FROM 
                  countries 
                WHERE
                  country_id = {country_id};
                ''')).fetchone()[0]
    author = await country_author(self, country_id=country_id)
    footer = interactions.EmbedFooter(text=
                                      f"/inventory give [Karbadia] [20 Drewno, 300 Talary] | "
                                      f"/inventory item [Drewno]")

    embeds = []
    for page in pages:
        embeds.append(interactions.Embed(
            title="Magazyny państwa",
            description=page,
            author=author,
            footer=footer,
            color=int(country_color, 16)
        ))
    return embeds
