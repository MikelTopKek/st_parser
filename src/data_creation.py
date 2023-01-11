import json

import requests
from sqlalchemy import MetaData, create_engine

from src.models import Item, Session, ItemType, MarketStats, engine, session

ITEM_NAMES_URL = "https://smartytitans.com/assets/gameData/texts_en.json"
ITEM_SHOP_URL = "https://smartytitans.com/assets/gameData/items.json"
ITEM_LIVE_URL = "https://smartytitans.com/api/item/last/all"
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


def create_marketstats_item(item_data, item):
    new_item_market_stats = MarketStats(**item_data)
    local_session.add(new_item_market_stats)
    item.marketstats.append(new_item_market_stats)
    local_session.commit()


def get_metadata():
    # get_raw_data()
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

    # get_fresh_data()

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


def create_live_data():

    get_live_data()

    with open("live_data.json", 'r') as file:
        data = json.load(file)

        for live_item in data["data"]:
            # item = Item.query.get(live_item["uid"])
            if live_item["tType"] == "o":
                try:
                    item = session.query(Item).get(live_item["uid"])
                    item_data = {
                         'item_id': item.uid,
                         'gold_price': live_item["goldPrice"],
                         'gold_qty': live_item["goldQty"],
                         'gems_price': live_item["gemsPrice"],
                         'gems_qty': live_item["gemsQty"],
                         'received_at': live_item["createdAt"],
                    }
                    create_marketstats_item(item_data, item)
                except Exception:
                    print(f'Error with {live_item["uid"]}')
