from sqlalchemy import (MetaData, create_engine)

from .data_creation import (create_live_data, get_optimal_items, get_best_airship_item, get_best_blue_seven_items)


meta = MetaData()


def main():
    engine = create_engine('postgresql+psycopg2://postgres:postgres@db:5432/postgres')
    # creating_data()
    # get_item_details()
    create_live_data()
    # get_optimal_items(additional_limit=5)
    # get_best_airship_item(min_airship_power=100)
    get_best_blue_seven_items(20)

    with engine.connect() as conn:
        with conn.begin():
            meta.create_all(engine)
    engine.dispose()

