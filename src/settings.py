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

worker_lvl_crafting_bonus_list = [0, 0, 1, 3, 4, 6, 7, 9, 10, 12, 13, 15, 16, 18, 19, 21, 22, 24, 25, 27, 28, 30,
                                  31, 33, 34, 36, 37, 39, 40, 42, 43, 45, 46, 48, 49, 51, 52, 54, 55, 67, 60]

workers_lvl = {'sun_dragon': os.getenv('SUN_DRAGON_LVL'),
               'priestess': os.getenv('PRIESTESS_LVL'),
               'master': os.getenv('MASTER_LVL'),
               'wizard': os.getenv('WIZARD_LVL'),
               'herbalist': os.getenv('HERBALIST_LVL'),
               'blacksmith': os.getenv('BLACKSMITH_LVL'),
               'jeweler': os.getenv('JEWELER_LVL'),
               'cook': os.getenv('COOK_LVL'),
               'carpenter': os.getenv('CARPENTER_LVL'),
               'tailor': os.getenv('TAILOR_LVL'),
               }

guild_bonus_craft_speed = 1 - int(os.getenv('GUILD_BONUS_CRAFT_SPEED'))*0.01


item_table = Item.__table__
market_stats = MarketStats.__table__
