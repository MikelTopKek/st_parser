import json
import logging.config

import pandas as pd

from src.constants import (DATA_SPREADSHEED_FILENAME, ITEM_LIVE_URL,
                           ITEM_NAMES_URL, ITEM_SHOP_URL)
from src.database_requests import items_list
from src.models import Item, ItemQuality, ItemType, MarketStats
from src.settings import (LOGGING, fresh_data_file, item_details_file,
                          live_data_file, raw_data_file, session)
from src.utils import (check_is_none, format_number, get_data,
                       quality_price_increase)

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('main_logger')
error_logger = logging.getLogger('error_logger')


def get_raw_data() -> None:
    """Get raw items data (names and uid).
    """
    get_data(ITEM_NAMES_URL, raw_data_file)


def get_fresh_data() -> None:
    """Get a fresh item data (all fields of item except bonus_crafting_time, receipt_availability and energy) .
    """
    get_data(ITEM_SHOP_URL, fresh_data_file)


def get_live_data() -> None:
    """Get actual items from market which are currently on sale.
    """
    logger.info("Getting live data...")
    get_data(ITEM_LIVE_URL, live_data_file)


def create_item(item_data: dict) -> None:
    """Create a new item in the database .

    Args:
        item_data (dict): item`s data
    """

    if session.query(Item).filter(Item.uid == item_data['uid']).scalar():
        logger.info(f'Item {item_data["uid"]} already exists, skipping...')
        return

    new_item = Item(**item_data)
    session.add(new_item)
    session.commit()
    logger.info('Item %s %s succesfully created!', item_data["uid"], item_data["tier"])


def update_item(excel_item: dict) -> None:
    """Update an item with data from excel spreadsheet .

    Args:
        excel_item (dict): dict with item data from .xlsx file
    """
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


def create_marketstats_item(item_data: dict) -> None:
    """Create a new MarketStats item which is currently on sale.

    Args:
        item_data (dict): item`s data with MarketStats fields
    """
    new_item_market_stats = MarketStats(**item_data)
    session.add(new_item_market_stats)
    session.commit()


def get_metadata() -> tuple:
    """Extract item metadata from raw data file

    Returns:
        tuple: returns item names and values
    """
    get_raw_data()

    with open(raw_data_file, encoding='UTF-8') as file:
        data = json.load(file)
        items = {}

        for field in data["texts"]:
            items[field] = data["texts"][field]
        item_names = []
        item_values = []

        for i, field in enumerate(items):
            if 8844 <= i <= 11300:
                if field.find("_name_o") == -1 and field.find("_name") != -1:
                    name = field.replace("_name", "")
                    item_names.append(name)
                    item_values.append(items[field])

    return item_names, item_values


def creating_data() -> None:
    """Creates a new items from fresh data
    """
    item_names, item_values = get_metadata()

    get_fresh_data()

    item_values_dict: dict = dict(zip(item_names, item_values))
    with open(fresh_data_file, encoding='UTF-8') as file:
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
            except KeyError as e:
                error_logger.error(str(e))


def create_live_data() -> None:
    """Create all live items in the database which are currently on sale
    """
    get_live_data()

    with open(live_data_file, encoding='UTF-8') as file:
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

                    except KeyError as error:
                        error_logger.error(f'Error with creating item {live_item["uid"]}. {str(error)}')
                    continue


def get_section_item(name: str, min_exp: float, limit: int,
                     tier: int, setup: list, max_cost_of_1m_exp: int=1_000,
                     min_airship_power: int=0) -> list[float]:
    """Get an items with exact ItemType.

    Args:
        name (str): item name
        exp (float): item minimum experience
        limit (int): more limit -> more results displayed
        tier (int): items with less than or equal to tier will be displayed in the result
        setup (list): list of item types which request used to get items
        max_cost_of_1m_exp (int, optional): max cost of 1 million experience in millions gold. Defaults to 1_000.
        min_airship_power (int, optional): min airship power to display items with best airship power
            (if 0 - display best items to levelling). Defaults to 0.

    Returns:
        list[float]: avg price and avg experience of choosen items
    """
    res = items_list(min_exp=min_exp, limit=limit, tier=tier, setup=setup,
                     min_airship_power=min_airship_power, max_cost_of_1m_exp=max_cost_of_1m_exp)

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
    avg: list = []
    avg_exp: list = []
    for item in res:
        scale = quality_price_increase(item[4])

        try:
            airpower = ""
            million_exp_cost = f"{round((item[5]-item[8]) / item[3], 1):.{4}}M"
            million_exp_cost = f'{million_exp_cost}{"":.<4}|'
            gold_value = format_number(item[5])
            experience = format_number(item[3])

            if min_airship_power > 0:
                airpower = f"{item[7]*scale:.<8}|"
                million_exp_cost = ""
            # if (item[5] - item[8]) / item[3] > max_cost_of_1m_exp or item[3] < exp:
            #     continue
            logger.info(
                f"{item[1].value:.<16}| {item[2]:.<4}| {item[0]:.<25}| "
                f"{experience:.<10}| {item[4].value:.<10}| {gold_value:.<10}| {format_number(item[8]):.<9}| "
                f"{round((item[5] - item[8]) / pow(item[3], 2) * 10000, 2):.<5}| {million_exp_cost} {airpower}"
            )

            avg.append((item[5] - item[8]) / item[3])
            avg_exp.append(item[3])

        except KeyError:
            error_logger.error(
                f"Item {item[0]} {item[1]} {item[2]} {item[3]} {item[4]} {item[5]} is broken"
            )

    if len(avg) > 0 and min_airship_power == 0:
        logger.info(f"Avg cost exp(millions): {sum(avg)/len(avg):.{4}}M")
        return [sum(avg) / len(avg), sum(avg_exp) / len(avg_exp)]

    return [0, 0]


def add_item_details_json() -> None:
    """Add item details from excel to a JSON file .
    """

    excel_data_df = pd.read_excel(
        DATA_SPREADSHEED_FILENAME, sheet_name="Blueprints")
    json_str = excel_data_df.to_json(orient="records")

    with open(item_details_file, "w", encoding='UTF-8') as file:
        file.write(json_str)


def get_item_details() -> None:
    """Load item details from JSON file .
    """
    add_item_details_json()

    with open(item_details_file, encoding='UTF-8') as file:
        excel_json_data = json.load(file)

        for excel_item in excel_json_data:
            update_item(excel_item)
