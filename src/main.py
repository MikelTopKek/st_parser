import os
import sys

from sqlalchemy import MetaData

from .data_creation import create_live_data, creating_data, get_item_details
from .item_requests import (
    get_best_airship_item,
    get_best_blue_seven_items,
    get_optimal_items, get_clothes_exp, get_meal_exp, get_best_crafting_items,
)
from .receipt_changing import create_csv_with_blueprints, update_db_with_blueprints
from .settings import engine, LOGGING
import logging.config

meta = MetaData()

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('main_logger')


def main():
    request_type = sys.argv[1]
    tier = int(os.getenv("TIER"))
    additional_limit = int(os.getenv("ADDITIONAL_LIMIT"))
    min_airship_power = int(os.getenv("MIN_AIRSHIP_POWER"))
    min_exp = int(os.getenv("MIN_EXP"))
    max_cost_of_1m_exp = int(os.getenv('MAX_COST_OF_1M_EXP'))
    min_tier = int(os.getenv('MIN_TIER'))

    with engine.connect() as conn:
        with conn.begin():
            meta.create_all(engine)

    if request_type == "filling_data":
        logger.info("Filling db with data...")
        creating_data()
        get_item_details()

    elif request_type == "optimal_items":
        logger.info('Getting optimal items...')
        create_live_data()
        get_optimal_items(additional_limit=additional_limit,
                          tier=tier, min_exp=min_exp,
                          max_cost_of_1m_exp=max_cost_of_1m_exp)

    elif request_type == "best_airship_item":
        logger.info("Getting best items with highest airship power...")
        # create_live_data()
        get_best_airship_item(
            additional_limit=additional_limit,
            min_airship_power=min_airship_power,
            tier=tier,
        )

    elif request_type == "blue_seven_item":
        logger.info("Getting cheapest flawless and better tier 7+ items...")
        # create_live_data()
        get_best_blue_seven_items(20)

    elif request_type == "clothes_items":
        logger.info('Getting clothes worker experience')
        get_clothes_exp(limit=additional_limit, tier=tier)

    elif request_type == "meals_items":
        logger.info('Getting meals worker experience')
        get_meal_exp(limit=additional_limit, tier=tier)

    elif request_type == "best_craft":
        logger.info('Getting best crafting items')
        # create_live_data()
        get_best_crafting_items(
            limit=additional_limit, tier=tier, min_tier=min_tier)

    elif request_type == "get_blueprints":
        logger.info('Getting blueprints to ./datafiles/blueprints.csv')
        create_csv_with_blueprints()

    elif request_type == "confirm_blueprints":
        logger.info('Confirm blueprints from ./datafiles/blueprints.csv')
        update_db_with_blueprints()

    engine.dispose()
