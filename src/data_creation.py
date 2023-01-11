import json

import requests

from src.models import Item, Session, ItemType, ItemClass

ITEM_NAMES_URL = "https://smartytitans.com/assets/gameData/texts_en.json"
ITEM_SHOP_URL = "https://smartytitans.com/assets/gameData/items.json"
ITEM_LIVE_URL = "https://smartytitans.com/api/item/last/all"


def get_data(url, file_name):
    request = requests.get(url=url)
    data = request.json()
    json_data = json.dumps(data)
    f = file_name
    with open(f, 'w') as file:
        file.write(json_data)


def get_raw_data():
    get_data(ITEM_NAMES_URL, "data.json")


def get_fresh_data():
    get_data(ITEM_SHOP_URL, "fresh_data.json")


def create_item(item_data):
    local_session = Session()
    new_item = Item(**item_data)
    local_session.add(new_item)
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
            if 8844 <= i <= 10549:
                if field.find("_name_o") == -1 and field.find('_name') != -1:
                    name = field.replace("_name", "")
                    item_names.append(name)
                    item_values.append(items[field])

                elif field.find("_desc") != -1:
                    item_descriptions.append(field.replace("_desc", ""))

    return item_names, item_values, item_descriptions


def creating_data():
    item_names, item_values, item_descriptions = get_metadata()

    # print(*item_names, sep="\n")
    print(len(item_names))
    # print(*item_descriptions, sep="\n")
    print(len(item_descriptions))
    # print(*item_values, sep="\n")
    print(len(item_values))

    # get_fresh_data()

    temp_data = {
                 'name': 'name11123',
                 'tier': 12,
                 'item_class': ItemClass.weapon,
                 'item_type': ItemType.axe,
                 'image': 'image',
                 'base_gold_value': 300,
                 'merchant_exp': 125,
                 'worker_exp': 250,
                 'worker1': 'None',
                 'worker2': 'None',
                 'worker3': 'None',
                 'favor': 1000,
                 'airship_power': 1000,
                 'collection_score': 2,
                 'energy_score': 150,
                 'energy_cost': 150,
                 'base_crafting_time': "3000"
                 }

    create_item(temp_data)
    # with open("fresh_data.json", 'r') as file:
    #     data = json.load(file)
    #     items = {}
    #     item_type = []
    #     for field in data:
    #         # items[field] = data[field]["level"]
    #         item_type.append(data[field]["type"])
    #         # print(data[field]["level"])
    #     i = 0
    #     item_types = []
    #     # print(*item_type, sep="\n")
    #     print(len(item_type))
