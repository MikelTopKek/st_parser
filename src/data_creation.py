import datetime
import json
import os

import requests
from sqlalchemy import MetaData, create_engine, case

from src.models import Item, Session, ItemType, MarketStats, engine, session, ItemQuality

ITEM_NAMES_URL = "https://smartytitans.com/assets/gameData/texts_en.json"
ITEM_SHOP_URL = "https://smartytitans.com/assets/gameData/items.json"
ITEM_LIVE_URL = "https://smartytitans.com/api/item/last/all"
ITEM_DETAILS_URL =\
    "https://docs.google.com/spreadsheets/d/1WLa7X8h3O0-aGKxeAlCL7bnN8-FhGd3t7pz2RCzSg8c/edit#gid=1558235212"
local_session = session


def get_data(url, file_name):
    request = requests.get(url=url)
    data = request.json()
    json_data = json.dumps(data, indent=4)
    f = file_name
    with open(f, 'w') as file:
        file.write(json_data)


def get_raw_data():
    get_data(ITEM_NAMES_URL, "data.json")


def get_fresh_data():
    get_data(ITEM_SHOP_URL, "fresh_data.json")


def get_live_data():
    get_data(ITEM_LIVE_URL, "live_data.json")


def create_item(item_data):

    new_item = Item(**item_data)
    local_session.add(new_item)
    local_session.commit()


def update_item(excel_item):
    try:
        updated_item = session.query(Item).filter(Item.name == excel_item["Name"]).first()
        updated_item.airship_power = excel_item["Airship Power"]
        session.commit()
        print(updated_item.name, updated_item.airship_power)
    except Exception:
        print(f'Error with item {excel_item["Name"]}')


def create_marketstats_item(item_data):
    new_item_market_stats = MarketStats(**item_data)
    local_session.add(new_item_market_stats)
    local_session.commit()


def get_metadata():
    get_raw_data()
    with open("data.json", 'r') as file:
        data = json.load(file)
        items = {}
        for field in data['texts']:
            items[field] = data["texts"][field]
        item_names = []
        item_values = []
        item_descriptions = []
        for i, field in enumerate(items):
            if 8844 <= i <= 11300: #10549:
                if field.find("_name_o") == -1 and field.find('_name') != -1:
                    name = field.replace("_name", "")
                    item_names.append(name)
                    item_values.append(items[field])

                elif field.find("_desc") != -1:
                    item_descriptions.append(field.replace("_desc", ""))

    return item_names, item_values, item_descriptions


def creating_data():
    item_names, item_values, item_descriptions = get_metadata()

    get_fresh_data()

    item_values_dict = dict(zip(item_names, item_values))
    with open("fresh_data.json", 'r') as file:
        data = json.load(file)
        for field in data:
            if data[field]["uid"] in ['uncommon', 'flawless', 'epic', 'legendary']:
                continue
            item_data = {
                 'name': item_values_dict[data[field]["uid"]],
                 'uid': data[field]["uid"],
                 'tier': data[field]["tier"],
                 # 'item_class': ItemClass.weapon,
                 'item_type': ItemType[data[field]["type"]],
                 'image': 'image',
                 'base_gold_value': data[field]["value"],
                 'merchant_exp': data[field]["xp"],
                 'worker_exp': data[field]["craftXp"],
                 'worker1': data[field]["worker1"],
                 'worker2': data[field]["worker2"],
                 'worker3': data[field]["worker3"],
                 'favor': data[field]["favor"],
                 # 'airship_power': data[field]["type"],
                 # 'collection_score': data[field]["type"],
                 # 'energy_score': data[field]["speedup"],

                 'energy_cost': data[field]["speedup"],
                 'base_crafting_time': data[field]["time"],
                 }
            try:
                create_item(item_data)
            except Exception:
                print(Exception)


def check_is_none(number):
    if number is None:
        return 0
    else:
        return number


import traceback

def create_live_data():

    get_live_data()

    with open("live_data.json", 'r') as file:
        data = json.load(file)

        for live_item in data["data"]:
            # item = Item.query.get(live_item["uid"])
            if live_item["tType"] == "o":
                try:
                    item = session.query(Item).get(live_item["uid"])
                    if live_item["tag1"] is None:
                        quality = ItemQuality.common.value
                    else:
                        quality = live_item["tag1"]
                    item_data = {
                         'item_id': item.uid,
                         'quality': quality,
                         'gold_price': check_is_none(live_item["goldPrice"]),
                         'gold_qty': live_item["goldQty"],
                         'gems_price': check_is_none(live_item["gemsPrice"]),
                         'gems_qty': live_item["gemsQty"],
                         'received_at': live_item["createdAt"],
                    }
                    create_marketstats_item(item_data)
                except Exception:
                    print(traceback.format_exc())

import sqlalchemy as sa
from sqlalchemy.sql import func


def get_section_item(name, exp, limit, tier, setup, min_airship_power=0):

    item_table = Item.__table__
    market_stats = MarketStats.__table__
    conn = engine
    recent_date = conn.execute(
        sa.select([market_stats.c.created_at])
        .select_from(
            market_stats
        )
    .order_by(market_stats.c.created_at.desc()).limit(1)
    ).fetchall()

    res = conn.execute(
        sa.select([item_table.c.name,
                   item_table.c.item_type,
                   item_table.c.tier,
                   item_table.c.merchant_exp,
                   market_stats.c.quality,
                   market_stats.c.gold_price,
                   market_stats.c.created_at,
                   item_table.c.airship_power
                   ])
        .select_from(
            item_table.join(
                market_stats, item_table.c.uid == market_stats.c.item_id
            ))
        .filter(sa.and_(
            market_stats.c.created_at == recent_date[0][0],
            market_stats.c.gold_price > 0,
            item_table.c.item_type.in_(setup),
            item_table.c.merchant_exp > exp,
            item_table.c.tier <= tier,
            item_table.c.airship_power > min_airship_power,
            # market_stats.c.quality == ItemQuality.common
            )) #cte
        # .group_by(item_table.c.item_type)
        .order_by(
            case([
                (min_airship_power == 0, item_table.c.merchant_exp/market_stats.c.gold_price),
                (min_airship_power != 0, item_table.c.airship_power)
                  ]).desc()
        ).limit(limit)
    ).fetchall()

    print(name, '-'*50)
    for item in res:
        try:
            airpower = ""
            if min_airship_power > 0:
                airpower = f'Airpower: {item[7]}'
            print(f'Type:{item[1].value:.<15}| Tier:{item[2]:.<10}| Item:{item[0]:.<25}| '
                  f'Exp:{item[3]:.<10}| Quality:{item[4].value:.<10}| Gold:{item[5]:.<10}|'
                  f' Index:{item[5]/item[3]:.{3}} {airpower}')
        except Exception:
            print(f'Item {item[0]} {item[1]} {item[2]} {item[3]} {item[4]} {item[5]} is broken')
    print(len(res))

    return res


def get_optimal_items(min_airship_power=0, additional_limit=0):

    # Elements
    get_section_item("Elements", 20000, 5+additional_limit, 10,
                     [ItemType.z], min_airship_power
                     )

    # Breastplates
    get_section_item("Breastplates", 35000, 3+additional_limit, 10,
                     [ItemType.ah, ItemType.am, ItemType.al], min_airship_power
                     )

    # Helmets
    get_section_item("Helmets", 50000, 3+additional_limit, 10,
                     [ItemType.hh, ItemType.hm, ItemType.hl, ItemType.xc], min_airship_power
                     )

    # Weapons (on rack)
    get_section_item("Weapons on rack", 50000, 3+additional_limit, 10,
                     [ItemType.ws, ItemType.wa, ItemType.wm, ItemType.wp, ItemType.wt], min_airship_power
                     )

    # Weapons (on table)
    get_section_item("Weapons on table", 50000, 3+additional_limit, 10,
                     [ItemType.wd, ItemType.ww, ItemType.wc, ItemType.wg, ItemType.wb, ItemType.xs],
                     min_airship_power
                     )

    # Misc. armor
    get_section_item("Misc armor", 35000, 5+additional_limit, 10,
                     [ItemType.gh, ItemType.gl, ItemType.bh, ItemType.bl], min_airship_power
                     )

    # Accessories
    get_section_item("Accessories", 45000, 5+additional_limit, 10,
                     [ItemType.uh, ItemType.up, ItemType.us,
                      ItemType.xr, ItemType.xa, ItemType.xf,
                      ItemType.fm, ItemType.fd],
                     min_airship_power
                     )


def get_best_airship_item(max_tier):
    get_optimal_items(min_airship_power=max_tier, additional_limit=5)


def add_item_details_json():
    # request_url =
    # "https://docs.google.com/spreadsheets/d/1WLa7X8h3O0-aGKxeAlCL7bnN8-FhGd3t7pz2RCzSg8c/export?format=xlsx&id=1WLa7X8h3O0-aGKxeAlCL7bnN8-FhGd3t7pz2RCzSg8c"

    # if not os.path.isfile("NAMEFILE111"):
    #     response = requests.get(request_url)
    # requests.get(request_url)

    # excel2json.convert_from_file('data_spreadsheet.xlsx')
    import pandas

    excel_data_df = pandas.read_excel('data_spreadsheet.xlsx', sheet_name='Blueprints')

    json_str = excel_data_df.to_json(orient="records")

    # json_data_1 = json.dumps(json_str, indent=4)
    # print('Excel Sheet to JSON:\n', json_str)
    f = 'item_details.json'

    with open(f, 'w') as file:
        file.write(json_str)


def get_item_details():
    add_item_details_json()


    conn = engine
    with open("item_details.json", 'r') as file:
        excel_json_data = json.load(file)

        for excel_item in excel_json_data:
            update_item(excel_item)

