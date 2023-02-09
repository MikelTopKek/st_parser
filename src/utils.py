import json
import logging.config

import requests

from src.models import ItemQuality
from src.settings import LOGGING, worker_lvl_crafting_bonus_list, workers_lvl

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('main_logger')
error_logger = logging.getLogger('error_logger')


def get_data(url, file_name):
    request = requests.get(url=url, timeout=5)
    data = request.json()
    json_data = json.dumps(data, indent=4)
    with open(file_name, "w", encoding='UTF-8') as file:
        file.write(json_data)


def format_number(number: float) -> str:
    if number >= 1000000:
        return f"{round(number / 1000000, 1)}M"

    if number >= 1000:
        return f"{round(number / 1000, 1)}k"

    return str(round(number, 1))


def check_is_none(number):
    if number is None:
        return 0

    return number


def quality_price_increase(item):
    if item == ItemQuality.common:
        scale = 1
    elif item == ItemQuality.uncommon:
        scale = 1.25
    elif item == ItemQuality.flawless:
        scale = 1.5
    elif item == ItemQuality.epic:
        scale = 2
    else:
        scale = 3

    return scale


def worker_bonus_speed(worker):
    if worker == 'Empty' or worker is None:
        return 0

    try:
        level = int(workers_lvl[worker])
    except KeyError as e:
        error_logger.error(f'KeyError when worker_bonus_speed on {e}: {worker}')
        level = 0
    return worker_lvl_crafting_bonus_list[level] * 0.01


def all_workers_bonus_speed(worker1, worker2, worker3):
    bonus1 = 1 - worker_bonus_speed(worker1)
    bonus2 = 1 - worker_bonus_speed(worker2)
    bonus3 = 1 - worker_bonus_speed(worker3)
    return bonus1*bonus2*bonus3


def sigil_craft_cost(blue_items_avg_cost: float, moonstone_cost: float, material_cost: float) -> float:
    return blue_items_avg_cost + moonstone_cost * 2 + material_cost * 6
