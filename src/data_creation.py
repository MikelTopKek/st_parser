import json
import sqlalchemy as sa
import requests
from sqlalchemy import case
import pandas as pd
from src.models import (Item, ItemQuality, ItemType, MarketStats, engine, session)
import traceback


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
                 'item_type': ItemType[data[field]["type"]],
                 'image': 'image',
                 'base_gold_value': data[field]["value"],
                 'merchant_exp': data[field]["xp"],
                 'worker_exp': data[field]["craftXp"],
                 'worker1': data[field]["worker1"],
                 'worker2': data[field]["worker2"],
                 'worker3': data[field]["worker3"],
                 'favor': data[field]["favor"],
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





def create_live_data():

    get_live_data()

    with open("live_data.json", 'r') as file:
        data = json.load(file)

        for live_item in data["data"]:
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
                   item_table.c.airship_power,
                   item_table.c.base_gold_value,
                   ])
        .select_from(
            item_table.join(
                market_stats, item_table.c.uid == market_stats.c.item_id
            ))
        .filter(sa.and_(
            market_stats.c.created_at == recent_date[0][0],
            market_stats.c.gold_price > 0,
            item_table.c.item_type.in_(setup),
            item_table.c.tier <= tier,
            item_table.c.airship_power > min_airship_power,
            case([
                (min_airship_power != 0, item_table.c.item_type != ItemType.xf),
                (min_airship_power == 0, item_table.c.merchant_exp > exp)
                  ]),
            ))
        .order_by(
            case([
                (min_airship_power == 0, market_stats.c.gold_price/item_table.c.merchant_exp*(-1)),
                (min_airship_power != 0, item_table.c.airship_power)
                  ]).desc()
        ).limit(limit)
    ).fetchall()

    if min_airship_power > 0:
        print(f'Type{"":.<12}| Tier{"":.<0}| Item{"":.<21}| Exp{"":.<7}| Quality{"":.<3}|'
              f' Gold{"":.<6}| Index{"":.<0}| Airpower')
    else:
        print(f'Type{"":.<12}| Tier{"":.<0}| Item{"":.<21}| Exp{"":.<7}| Quality{"":.<3}|'
              f' Gold{"":.<6}| Index{"":.<0}| 1M EXP cost{"":.<0}|')
    avg = []
    for item in res:
        if item[4] == ItemQuality.common:
            scale = 1
        elif item[4] == ItemQuality.uncommon:
            scale = 1.25
        elif item[4] == ItemQuality.flawless:
            scale = 1.5
        elif item[4] == ItemQuality.epic:
            scale = 2
        else:
            scale = 3
        try:
            airpower = ""
            million_exp_cost = f"{(item[5]-item[8])/item[3]:.{4}}M"
            million_exp_cost = f'{million_exp_cost}{"":.<4}|'
            if min_airship_power > 0:
                airpower = f'Airpower: {item[7]*scale}'
                million_exp_cost = ""
            print(f'{item[1].value:.<16}| {item[2]:.<4}| {item[0]:.<25}| '
                  f'{item[3]:.<10}| {item[4].value:.<10}| {item[5]:.<10}| '
                  f'{item[5]/item[3]:.{4}}{"":.<1}| {million_exp_cost} {airpower}')
            avg.append((item[5]-item[8])/item[3])
        except Exception:
            print(f'Item {item[0]} {item[1]} {item[2]} {item[3]} {item[4]} {item[5]} is broken')
    if len(avg) > 0:
        print(f'Avg cost exp(millions): {sum(avg)/len(avg):.{4}}M')

    return res


def get_optimal_items(min_airship_power=0,  additional_limit=0, tier=11):

    # Elements
    get_section_item("Elements", 20000, 5+additional_limit, tier,
                     [ItemType.z], min_airship_power
                     )

    # Breastplates
    get_section_item("Breastplates", 35000, 3+additional_limit, tier,
                     [ItemType.ah, ItemType.am, ItemType.al], min_airship_power
                     )

    # Helmets
    get_section_item("Helmets", 50000, 3+additional_limit, tier,
                     [ItemType.hh, ItemType.hm, ItemType.hl, ItemType.xc], min_airship_power
                     )

    # Weapons (on rack)
    get_section_item("Weapons on rack", 50000, 3+additional_limit, tier,
                     [ItemType.ws, ItemType.wa, ItemType.wm, ItemType.wp, ItemType.wt], min_airship_power
                     )

    # Weapons (on table)
    get_section_item("Weapons on table", 50000, 3+additional_limit, tier,
                     [ItemType.wd, ItemType.ww, ItemType.wc, ItemType.wg, ItemType.wb, ItemType.xs],
                     min_airship_power
                     )

    # Misc. armor
    get_section_item("Misc armor", 35000, 5+additional_limit, tier,
                     [ItemType.gh, ItemType.gl, ItemType.bh, ItemType.bl], min_airship_power
                     )

    # Accessories
    get_section_item("Accessories", 45000, 5+additional_limit, tier,
                     [ItemType.uh, ItemType.up, ItemType.us,
                      ItemType.xr, ItemType.xa, ItemType.xf,
                      ItemType.fm, ItemType.fd],
                     min_airship_power
                     )


def get_best_airship_item(min_airship_power):
    get_optimal_items(min_airship_power=min_airship_power, additional_limit=10)


def add_item_details_json():
    # request_url =
    # "https://docs.google.com/spreadsheets/d/1WLa7X8h3O0-aGKxeAlCL7bnN8-FhGd3t7pz2RCzSg8c/export?format=xlsx&id=1WLa7X8h3O0-aGKxeAlCL7bnN8-FhGd3t7pz2RCzSg8c"

    excel_data_df = pd.read_excel('data_spreadsheet.xlsx', sheet_name='Blueprints')

    json_str = excel_data_df.to_json(orient="records")

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


def get_best_blue_seven_items(limit):

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
                   ])
        .select_from(
            item_table.join(
                market_stats, item_table.c.uid == market_stats.c.item_id
            )
        )
        .filter(sa.and_(
            market_stats.c.created_at == recent_date[0][0],
            market_stats.c.gold_price > 0,
            item_table.c.tier >= 7,
            market_stats.c.quality != ItemQuality.common,
            market_stats.c.quality != ItemQuality.uncommon,
        ))
        .order_by(market_stats.c.gold_price)
        .limit(limit)
    ).fetchall()

    print(f'Type{"":.<12}| Tier{"":.<0}| Item{"":.<21}| Quality{"":.<3}| Gold{"":.<6}|')
    for item in res:
        try:
            print(f'{item[1].value:.<16}| {item[2]:.<4}| {item[0]:.<25}| '
                  f'{item[4].value:.<10}| {item[5]/1000:{1}}k{"":.<10}|')
        except Exception:
            print(f'Item {item[0]} {item[1]} {item[2]} {item[3]} {item[4]} {item[5]} is broken')

    return res
