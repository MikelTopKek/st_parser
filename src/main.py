import psycopg2
from sqlalchemy import (Column, Integer, MetaData, String, Table,
                        create_engine, text)

from src.selenium_base import parse

from .data_creation import create_live_data, creating_data, get_optimal_items, get_item_details, get_best_airship_item
from .models import Base, Item, MarketStats

meta = MetaData()


def main():
    engine = create_engine('postgresql+psycopg2://postgres:postgres@db:5432/postgres')
    # creating_data()
    # get_item_details()
    # create_live_data()
    get_optimal_items(additional_limit=10)
    # get_best_airship_item(max_tier=100)
    with engine.connect() as conn:
        # conn = conn.execution_options(isolation_level="")
        # Transaction isolation level
        with conn.begin():
            # students = Table(
            #     'students', meta,
            #     Column('id', Integer, primary_key=True),
            #     Column('name', String),
            #     Column('lastname', String),
            # )
            meta.create_all(engine)
            # import datetime
            # conn.execute(f"insert into students (name, lastname) values ('{datetime.datetime.now()}', 'test')")
        # with conn.begin():
        #     res = conn.execute('select *')
        #     print(res.fetchall())
            # conn.execute('insert into students(id, name, ')
    engine.dispose()
        # parse()
