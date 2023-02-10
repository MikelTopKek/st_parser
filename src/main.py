import logging.config
import sys

from sqlalchemy import MetaData

from .data_creation import create_live_data, creating_data, get_item_details
from .item_requests import (get_best_airship_item, get_best_blue_seven_items,
                            get_best_crafting_items, get_clothes_exp,
                            get_meal_exp, get_optimal_items)
from .receipt_changing import (create_csv_with_blueprints,
                               update_db_with_blueprints)
from .settings import (ADDITIONAL_LIMIT, LOGGING, MAX_COST_OF_1M_EXP,
                       MIN_AIRSHIP_POWER, MIN_EXP, MIN_TIER, TIER, engine)

meta = MetaData()

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('main_logger')


def main() -> None:
    request_type: str = sys.argv[1]

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
        get_optimal_items(additional_limit=ADDITIONAL_LIMIT,
                          tier=TIER, min_exp=MIN_EXP,
                          max_cost_of_1m_exp=MAX_COST_OF_1M_EXP)

    elif request_type == "best_airship_item":
        logger.info("Getting best items with highest airship power...")
        create_live_data()
        get_best_airship_item(
            additional_limit=ADDITIONAL_LIMIT,
            min_airship_power=MIN_AIRSHIP_POWER,
            tier=TIER,
        )

    elif request_type == "blue_seven_item":
        logger.info("Getting cheapest flawless and better tier 7+ items...")
        create_live_data()
        get_best_blue_seven_items(20)

    elif request_type == "clothes_items":
        logger.info('Getting clothes worker experience')
        get_clothes_exp(limit=ADDITIONAL_LIMIT, tier=TIER)

    elif request_type == "meals_items":
        logger.info('Getting meals worker experience')
        get_meal_exp(limit=ADDITIONAL_LIMIT, tier=TIER)

    elif request_type == "best_craft":
        logger.info('Getting best crafting items')
        create_live_data()
        get_best_crafting_items(
            limit=ADDITIONAL_LIMIT, tier=TIER, min_tier=MIN_TIER)

    elif request_type == "get_blueprints":
        logger.info('Getting blueprints to ./datafiles/blueprints.csv')
        create_csv_with_blueprints()

    elif request_type == "confirm_blueprints":
        logger.info('Confirm blueprints from ./datafiles/blueprints.csv')
        update_db_with_blueprints()

    engine.dispose()
