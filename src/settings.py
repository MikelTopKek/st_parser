import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Item, MarketStats

engine = create_engine(
    "postgresql+psycopg2://postgres:postgres@db:5432/postgres")
Session = sessionmaker(bind=engine)
session = Session()

ITEM_NAMES_URL = "https://smartytitans.com/assets/gameData/texts_en.json"
ITEM_SHOP_URL = "https://smartytitans.com/assets/gameData/items.json"
ITEM_LIVE_URL = "https://smartytitans.com/api/item/last/all"
ITEM_DETAILS_URL = "https://docs.google.com/spreadsheets/d/1WLa7X8h3O0-aGKxeAlCL7bnN8-FhGd3t7pz2RCzSg8c/edit#gid=1558235212"

raw_data_file = os.getenv("RAW_DATA_FILENAME")
fresh_data_file = os.getenv("FRESH_DATA_FILENAME")
live_data_file = os.getenv("LIVE_DATA_FILENAME")
output_file = os.getenv("OUTPUT_FILENAME")
item_details_file = os.getenv("ITEM_DETAILS_NAME")
data_spreadsheet_file = os.getenv("DATA_SPREADSHEED_FILENAME")


item_table = Item.__table__
market_stats = MarketStats.__table__
