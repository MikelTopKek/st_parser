import json

import pandas as pd

from src.database_requests import items_list
from src.models import Item, ItemQuality, ItemType, MarketStats
from src.settings import (
    ITEM_LIVE_URL,
    ITEM_NAMES_URL,
    ITEM_SHOP_URL,
    data_spreadsheet_file,
    fresh_data_file,
    item_details_file,
    live_data_file,
    raw_data_file,
    session, LOGGING,
)
from src.utils import check_is_none, format_number, get_data, quality_price_increase
import logging.config


logging.config.dictConfig(LOGGING)
logger = logging.getLogger('main_logger')
error_logger = logging.getLogger('error_logger')


def get_raw_data():
    get_data(ITEM_NAMES_URL, raw_data_file)


def get_fresh_data():
    get_data(ITEM_SHOP_URL, fresh_data_file)


def get_live_data():
    logger.info("Getting live data...")
    get_data(ITEM_LIVE_URL, live_data_file)


def create_item(item_data):

    if session.query(Item).filter(Item.uid == item_data['uid']).scalar():
        logger.info(f'Item {item_data["uid"]} already exists, skipping...')
        return

    new_item = Item(**item_data)
    session.add(new_item)
    session.commit()
    logger.info('Item %s %s succesfully created!', item_data["uid"], item_data["tier"])


def update_item(excel_item):
    try:
        updated_item = (
            session.query(Item).filter(Item.name == excel_item["Name"]).first()
        )
        if updated_item.airship_power == excel_item["Airship Power"]:
            logger.info(f'Item {updated_item.name} alredy have the same airship power. Skipping...')
            return
        updated_item.airship_power = excel_item["Airship Power"]
        if updated_item.worker2 is None:
            updated_item.worker2 = "Empty"
        if updated_item.worker3 is None:
            updated_item.worker3 = "Empty"
        session.commit()
        logger.info(f'Item {updated_item.name} updated with airship power {updated_item.airship_power} successfully!')
    except TypeError as e:
        error_logger.error(f'Error with item {excel_item["Name"]} Exc:{str(e)}')


def create_marketstats_item(item_data):

    new_item_market_stats = MarketStats(**item_data)
    session.add(new_item_market_stats)
    session.commit()


def get_metadata():
    get_raw_data()
    with open(raw_data_file) as file:
        data = json.load(file)
        items = {}
        for field in data["texts"]:
            items[field] = data["texts"][field]
        item_names = []
        item_values = []
        item_descriptions = []
        for i, field in enumerate(items):
            if 8844 <= i <= 11300:
                if field.find("_name_o") == -1 and field.find("_name") != -1:
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
    with open(fresh_data_file) as file:
        data = json.load(file)
        for field in data:
            if data[field]["uid"] in ["uncommon", "flawless", "epic", "legendary"]:
                continue
            item_data = {
                "name": item_values_dict[data[field]["uid"]],
                "uid": data[field]["uid"],
                "tier": data[field]["tier"],
                "item_type": ItemType[data[field]["type"]],
                "image": "image",
                "base_gold_value": data[field]["value"],
                "merchant_exp": data[field]["xp"],
                "worker_exp": data[field]["craftXp"],
                "worker1": data[field]["worker1"],
                "worker2": data[field]["worker2"],
                "worker3": data[field]["worker3"],
                "favor": data[field]["favor"],
                "energy_cost": data[field]["speedup"],
                "base_crafting_time": data[field]["time"],
            }
            try:
                create_item(item_data)
            except Exception as e:
                error_logger.error(str(e))


def create_live_data():

    get_live_data()

    with open(live_data_file) as file:
        data = json.load(file)

        for live_item in data["data"]:
            if live_item["tType"] in ["o", "os"]:
                try:
                    item = session.query(Item).get(live_item["uid"])

                    if live_item["tag1"] is None:
                        quality = ItemQuality.common.value
                    else:
                        quality = live_item["tag1"]
                    item_data = {
                        "item_id": item.uid,
                        "quality": quality,
                        "gold_price": check_is_none(live_item["goldPrice"]),
                        "gold_qty": live_item["goldQty"],
                        "gems_price": check_is_none(live_item["gemsPrice"]),
                        "gems_qty": live_item["gemsQty"],
                        "received_at": live_item["createdAt"],
                    }
                    create_marketstats_item(item_data)
                except AttributeError as e:
                    logger.info(
                        f'uid:{live_item["uid"]} tier:{live_item["tier"]} {live_item["tType"]} doesn`t exist. '
                        f'Error: {str(e)} '
                        f'Trying to create it in db...')
                    item_data = {
                        "name": live_item["uid"],
                        "uid": live_item["uid"],
                        "tier": live_item["tier"],
                        "item_type": ItemType.xm,
                        "image": "image",
                    }
                    try:
                        create_item(item_data)
                        logger.info(f'Succesfully created {live_item["uid"]} in db.')
                    except Exception as e:
                        error_logger.error(f'Error with creating item {live_item["uid"]}. {str(e)}')
                    continue


def get_section_item(name, exp, limit, tier, setup, max_cost_of_1m_exp=1e3, min_airship_power=0):
    res = items_list(exp, limit, tier, setup,
                     min_airship_power, max_cost_of_1m_exp)

    logger.info(f"{name}")
    if min_airship_power > 0:
        logger.info(
            f'Type{"":.<12}| Tier{"":.<0}| Item{"":.<21}| Exp{"":.<7}| Quality{"":.<3}|'
            f' Gold{"":.<6}| Base gold| Index| Airpower|'
        )
    else:
        logger.info(
            f'Type{"":.<12}| Tier{"":.<0}| Item{"":.<21}| Exp{"":.<7}| Quality{"":.<3}|'
            f' Gold{"":.<6}| Base gold| Index| 1M EXP cost{"":.<0}|'
        )
    avg = []
    avg_exp = []
    for item in res:
        scale = quality_price_increase(item[4])
        try:
            airpower = ""
            million_exp_cost = f"{round((item[5]-item[8])/item[3], 1):.{4}}M"
            million_exp_cost = f'{million_exp_cost}{"":.<4}|'
            gold_value = format_number(item[5])
            experience = format_number(item[3])
            if min_airship_power > 0:
                airpower = f"{item[7]*scale:.<8}|"
                million_exp_cost = ""
            logger.info(
                f"{item[1].value:.<16}| {item[2]:.<4}| {item[0]:.<25}| "
                f"{experience:.<10}| {item[4].value:.<10}| {gold_value:.<10}| {format_number(item[8]):.<9}| "
                f"{round((item[5] - item[8]) / pow(item[3], 2) * 10000, 2):.<5}| {million_exp_cost} {airpower}"
            )
            avg.append((item[5] - item[8]) / item[3])
            avg_exp.append(item[3])
        except Exception:
            error_logger.error(
                f"Item {item[0]} {item[1]} {item[2]} {item[3]} {item[4]} {item[5]} is broken"
            )
    if len(avg) > 0 and min_airship_power == 0:
        logger.info(f"Avg cost exp(millions): {sum(avg)/len(avg):.{4}}M")
        return [sum(avg) / len(avg), sum(avg_exp) / len(avg_exp)]
    else:
        return [0, 0]


def add_item_details_json():

    excel_data_df = pd.read_excel(
        data_spreadsheet_file, sheet_name="Bluelogger.infos")
    json_str = excel_data_df.to_json(orient="records")

    logger.info(json_str)


def get_item_details():
    add_item_details_json()
    with open(item_details_file) as file:
        excel_json_data = json.load(file)

        for excel_item in excel_json_data:
            update_item(excel_item)
