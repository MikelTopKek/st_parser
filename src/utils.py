import json
import logging.config
from typing import Optional

import requests

from src.models import ItemQuality
from src.numeric_utils import to_int
from src.settings import LOGGING, worker_lvl_crafting_bonus_list, workers_lvl

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('main_logger')
error_logger = logging.getLogger('error_logger')


def get_data(url: str, file_name: Optional[str]) -> None:
    """Download data from url .

    Args:
        url (str): url
        file_name (Optional[str]): output file name
    """
    request = requests.get(url=url, timeout=5)
    data = request.json()
    json_data = json.dumps(data, indent=4)
    with open(file_name, "w", encoding='UTF-8') as file:
        file.write(json_data)


def format_number(number: float) -> str:
    """Format a number into a human readable string .

    Args:
        number (float): number

    Returns:
        str: formatted string
    """
    if number >= 1000000:
        return f"{round(number / 1000000, 1)}M"

    if number >= 1000:
        return f"{round(number / 1000, 1)}k"

    return str(round(number, 1))


def check_is_none(number: int) -> int:
    """Check if number is None .

    Args:
        number (int): number

    Returns:
        int: 0 or number
    """
    if number is None:
        return 0

    return number


def quality_price_increase(item: ItemQuality) -> float:
    """Increase the quality of a given item.

    Args:
        item (ItemQuality): item`s quality

    Returns:
        float: scaling number for item due to it`s quality
    """
    scale: float
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


def worker_bonus_speed(worker: str) -> float:
    """Returns the bonus speed by worker .

    Args:
        worker (str): worker`s name

    Returns:
        float: craft speed bonus
    """
    if worker == 'Empty' or worker is None:
        return 0

    try:
        level = to_int(workers_lvl[worker])
    except KeyError as e:
        error_logger.error(f'KeyError when worker_bonus_speed on {e}: {worker}')
        level = 0
    return worker_lvl_crafting_bonus_list[level] * 0.01


def all_workers_bonus_speed(worker1: str, worker2: str, worker3: str) -> float:
    """Calculates the bonus speed of all workers .

    Args:
        worker1 (str): worker1`s name
        worker2 (str): worker2`s name
        worker3 (str): worker3`s name

    Returns:
        float: summary craft speed bonus
    """
    bonus1 = 1 - worker_bonus_speed(worker1)
    bonus2 = 1 - worker_bonus_speed(worker2)
    bonus3 = 1 - worker_bonus_speed(worker3)
    return bonus1*bonus2*bonus3


def sigil_craft_cost(blue_items_avg_cost: float, moonstone_cost: float, material_cost: float) -> float:
    return blue_items_avg_cost + moonstone_cost * 2 + material_cost * 6
