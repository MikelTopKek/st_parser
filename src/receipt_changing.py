import logging.config

import pandas as pd

from src.database_requests import items_with_blueprints
from src.models import Item
from src.settings import LOGGING, session

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('main_logger')
error_logger = logging.getLogger('error_logger')


def create_csv_with_blueprints():
    res = items_with_blueprints()
    blueprints_dict: list[dict] = []

    for item in res:
        blueprints_dict.append({
            'name': item[0],
            'item_type':  item[1].value,
            'tier': item[2],
            'uid': item[3],
            'receipt_availability': 1 if item[4] else 0
        })

    raw_data = pd.DataFrame(blueprints_dict)
    raw_data.to_csv('./datafiles/blueprints.csv')
    # print(raw_data)

    return raw_data


def update_db_with_blueprints():

    blueprints = pd.read_csv('./datafiles/blueprints.csv', header=None, index_col=0, on_bad_lines='skip')
    my_dict = blueprints.to_dict(orient='records')

    my_dict.pop(0)

    for item in my_dict:

        try:
            updated_item = (
                session.query(Item).filter(Item.uid == item[4]).first()
            )

            if updated_item.receipt_availability != int(item[5]):
                updated_item.receipt_availability = bool(int(item[5]))
                logger.info(f'Update {updated_item.name}, availability now is {updated_item.receipt_availability}')

        except KeyError as e:
            error_logger.error(f'{str(e)} with item {item[4]}')

        session.commit()
