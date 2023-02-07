import json

import requests

from src.models import ItemQuality
from src.settings import workers_lvl, worker_lvl_crafting_bonus_list


def get_data(url, file_name):
    request = requests.get(url=url)
    data = request.json()
    json_data = json.dumps(data, indent=4)
    f = file_name
    with open(f, "w") as file:
        file.write(json_data)


def format_number(number: int) -> str:
    if number >= 1000000:
        return f"{round(number / 1000000, 1)}M"
    elif number >= 1000:
        return f"{round(number / 1000, 1)}k"
    else:
        return str(number)


def check_is_none(number):
    if number is None:
        return 0
    else:
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
    if worker == 'Empty':
        return 0
    else:
        try:
            level = int(workers_lvl[worker])
        except KeyError as e:
            print(f'KeyError when worker_bonus_speed on {e}: {worker}')
            level = 0
        return worker_lvl_crafting_bonus_list[level] * 0.01


def all_workers_bonus_speed(worker1, worker2, worker3):
    bonus1 = 1 - worker_bonus_speed(worker1)
    bonus2 = 1 - worker_bonus_speed(worker2)
    bonus3 = 1 - worker_bonus_speed(worker3)
    return bonus1*bonus2*bonus3
