import os
import sys

from sqlalchemy import MetaData

from .data_creation import create_live_data, creating_data, get_item_details
from .item_requests import (
    get_best_airship_item,
    get_best_blue_seven_items,
    get_optimal_items, get_clothes_exp,
)
from .settings import engine

meta = MetaData()


def main():
    request_type = sys.argv[1]
    tier = int(os.getenv("TIER"))
    additional_limit = int(os.getenv("ADDITIONAL_LIMIT"))
    min_airship_power = int(os.getenv("MIN_AIRSHIP_POWER"))
    min_exp = int(os.getenv("MIN_EXP"))
    open(os.getenv("OUTPUT_FILENAME"), "w").close()

    with engine.connect() as conn:
        with conn.begin():
            meta.create_all(engine)

    if request_type == "filling_data":
        print("Filling db with data...")
        creating_data()
        get_item_details()
    elif request_type == "optimal_items":
        print("Getting optimal items...")
        create_live_data()
        get_optimal_items(additional_limit=additional_limit,
                          tier=tier, min_exp=min_exp)
    elif request_type == "best_airship_item":
        print("Getting best items with highest airship power...")
        create_live_data()
        get_best_airship_item(
            additional_limit=additional_limit,
            min_airship_power=min_airship_power,
            tier=tier,
        )
    elif request_type == "blue_seven_item":
        print("Getting cheapest flawless and better tier 7+ items...")
        create_live_data()
        get_best_blue_seven_items(20)
    elif request_type == "clothes_items":
        print('Getting clothes merchant experience')
        get_clothes_exp(limit=additional_limit, tier=tier)
    engine.dispose()
