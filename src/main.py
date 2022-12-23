from sqlalchemy.ext.declarative import declarative_base

from src.selenium_base import parse
from sqlalchemy import create_engine, text
import psycopg2
from sqlalchemy import Table, Column, Integer, String, MetaData
from .classes import Item, MarketStats

meta = MetaData()
Base = declarative_base()


def main():
    engine = create_engine('postgresql+psycopg2://postgres:postgres@db:5432/postgres')
    Base.metadata.create_all(engine)
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

        # parse()
