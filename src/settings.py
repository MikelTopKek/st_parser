import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Item, MarketStats

load_dotenv()

DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_PORT = os.getenv('DATABASE_PORT')
POSTGRES_DB = os.getenv('POSTGRES_DB')
DATABASE_ENGINE = os.getenv('DATABASE_ENGINE')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')


engine = create_engine(
    f"{DATABASE_ENGINE}://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{POSTGRES_DB}")
Session = sessionmaker(bind=engine)
session = Session()

ITEM_NAMES_URL = "https://smartytitans.com/assets/gameData/texts_en.json"
ITEM_SHOP_URL = "https://smartytitans.com/assets/gameData/items.json"
ITEM_LIVE_URL = "https://smartytitans.com/api/item/last/all"
ITEM_DETAILS_URL = "https://docs.google.com/" \
    "spreadsheets/d/1WLa7X8h3O0-aGKxeAlCL7bnN8-FhGd3t7pz2RCzSg8c/edit#gid=1558235212"


raw_data_file = os.getenv("RAW_DATA_FILENAME")
fresh_data_file = os.getenv("FRESH_DATA_FILENAME")
live_data_file = os.getenv("LIVE_DATA_FILENAME")
item_details_file = os.getenv("ITEM_DETAILS_NAME")

SOLD_PER_HOUR = int(os.getenv("SOLD_PER_HOUR"))
NEEDED_EXP = int(os.getenv("NEEDED_EXP"))
NUMBER_OF_CRAFT_SLOTS = int(os.getenv('NUMBER_OF_CRAFT_SLOTS'))

TIER = int(os.getenv("TIER"))
ADDITIONAL_LIMIT = int(os.getenv("ADDITIONAL_LIMIT"))
MIN_EXP = int(os.getenv("MIN_EXP"))
MIN_AIRSHIP_POWER = int(os.getenv("MIN_AIRSHIP_POWER"))
MAX_COST_OF_1M_EXP = int(os.getenv('MAX_COST_OF_1M_EXP'))
MIN_TIER = int(os.getenv('MIN_TIER'))

worker_lvl_crafting_bonus_list = [0, 0, 1, 3, 4, 6, 7, 9, 10, 12, 13, 15, 16, 18, 19, 21, 22, 24, 25, 27, 28, 30,
                                  31, 33, 34, 36, 37, 39, 40, 42, 43, 45, 46, 48, 49, 51, 52, 54, 55, 67, 60]

workers_lvl = {'sun_dragon': os.getenv('SUN_DRAGON_LVL'),
               'priest': os.getenv('PRIESTESS_LVL'),
               'master': os.getenv('MASTER_LVL'),
               'wizard': os.getenv('WIZARD_LVL'),
               'herbalist': os.getenv('HERBALIST_LVL'),
               'blacksmith': os.getenv('BLACKSMITH_LVL'),
               'jeweler': os.getenv('JEWELER_LVL'),
               'cook': os.getenv('COOK_LVL'),
               'carpenter': os.getenv('CARPENTER_LVL'),
               'tailor': os.getenv('TAILOR_LVL'),
               'baker': os.getenv('BAKER_LVL')
               }

guild_bonus_craft_speed = 1 - int(os.environ.get('GUILD_BONUS_CRAFT_SPEED')) * 0.01


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'main_formatter': {
            'format': '%(asctime)s %(levelname)-3s |%(message)s',
            'datefmt': '%m-%d %H:%M'
        },
        'error_formatter': {
            'format': '%(asctime)s %(levelname)-3s [%(filename)s:%(lineno)d] |%(message)s',
            'datefmt': '%m-%d %H:%M'
        },
    },
    'handlers': {
        'main_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'main_formatter'
        },
        'error_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'error_formatter'
        },
    },
    'loggers': {
        'main_logger': {
            'level': 'INFO',
            'handlers': ['main_handler']
        },
        'error_logger': {
            'level': 'ERROR',
            'handlers': ['error_handler']
        },
    }
}


item_table = Item.__table__
market_stats = MarketStats.__table__
