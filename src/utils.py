import json

import requests

from src.models import ItemQuality


def get_data(url, file_name):
    request = requests.get(url=url)
    data = request.json()
    json_data = json.dumps(data, indent=4)
    f = file_name
    with open(f, 'w') as file:
        file.write(json_data)


def format_number(number):
    if number > 1000000:
        return f'{round(number / 1000000, 2)}M'
    elif number > 1000:
        return f'{round(number / 1000, 2)}k'
    else:
        return number


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