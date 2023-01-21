import datetime
import os

from src.data_creation import get_section_item
from src.database_requests import best_blue_seven_plus_items_list, merchant_exp_request
from src.models import ItemType
from src.settings import guild_bonus_craft_speed
from src.utils import format_number, all_workers_bonus_speed


def get_best_blue_seven_items(limit):

    res = best_blue_seven_plus_items_list(limit)

    with open(os.getenv("OUTPUT_FILENAME"), "a") as file:
        file.write(
            f'Type{"":.<12}| Tier{"":.<0}| Item{"":.<21}| Quality{"":.<3}| Gold{"":.<6}|\n'
        )
        for item in res:
            try:
                gold_value = format_number(item[4])
                file.write(
                    f"{item[1].value:.<16}| {item[2]:.<4}| {item[0]:.<25}| "
                    f"{item[3].value:.<10}| {gold_value:.<10}|\n"
                )
            except Exception:
                file.write(
                    f"Item {item[0]} {item[1]} {item[2]} {item[3]} {item[4]} {item[5]} is broken"
                )

    return res


def get_optimal_items(min_airship_power=0, additional_limit=0, tier=0, min_exp=0):

    # Elements
    get_section_item(
        "Elements",
        min_exp,
        10 + additional_limit,
        tier,
        [ItemType.z],
        min_airship_power,
    )
    # Breastplates
    get_section_item(
        "Breastplates",
        min_exp * 1.2,
        3 + additional_limit,
        tier,
        [ItemType.ah, ItemType.am, ItemType.al],
        min_airship_power,
    )
    # Helmets
    get_section_item(
        "Helmets",
        min_exp * 1.5,
        3 + additional_limit,
        tier,
        [ItemType.hh, ItemType.hm, ItemType.hl, ItemType.xc],
        min_airship_power,
    )
    # Weapons (on rack)
    get_section_item(
        "Weapons on rack",
        min_exp * 1.5,
        3 + additional_limit,
        tier,
        [ItemType.ws, ItemType.wa, ItemType.wm, ItemType.wp, ItemType.wt],
        min_airship_power,
    )
    # Weapons (on table)
    get_section_item(
        "Weapons on table",
        min_exp * 1.5,
        3 + additional_limit,
        tier,
        [ItemType.wd, ItemType.ww, ItemType.wc,
            ItemType.wg, ItemType.wb, ItemType.xs],
        min_airship_power,
    )
    # Misc. armor
    get_section_item(
        "Misc armor",
        min_exp,
        5 + additional_limit,
        tier,
        [ItemType.gh, ItemType.gl, ItemType.bh, ItemType.bl],
        min_airship_power,
    )
    # Accessories
    get_section_item(
        "Accessories",
        min_exp * 1.4,
        5 + additional_limit,
        tier,
        [
            ItemType.uh,
            ItemType.up,
            ItemType.us,
            ItemType.xr,
            ItemType.xa,
            ItemType.xf,
            ItemType.fm,
            ItemType.fd,
        ],
        min_airship_power,
    )


def get_best_airship_item(additional_limit, min_airship_power, tier):
    get_optimal_items(
        additional_limit=additional_limit,
        min_airship_power=min_airship_power,
        tier=tier,
    )


def get_merchant_exp(limit, setup, tier):
    res = merchant_exp_request(limit, setup, tier)
    with open(os.getenv("OUTPUT_FILENAME"), "a") as file:
        file.write(
            f'Type{"":.<12}| Tier{"":.<0}| Item{"":.<21}| Exp{"":.<7}| '
            f'Worker1{"":.<3}| Worker2{"":.<3}| Worker3{"":.<3}| Crafting_time|\n'
        )
        for item in res:
            if item[7]:
                item_time = str(datetime.timedelta(
                    seconds=round(
                        int(item[7])*all_workers_bonus_speed(item[4], item[5], item[6]) * guild_bonus_craft_speed, 0)
                ))
            try:
                file.write(
                    f"{item[1].value:.<16}| {item[2]:.<4}| {item[0]:.<25}| "
                    f"{format_number(item[3]):.<10}| {item[4]:.<10}| {str(item[5]):.<10}|"
                    f" {str(item[6]):.<10}| {item_time:.<13}|\n"
                )
            except Exception:
                file.write(
                    f"Item {item[0]} {item[1]} {item[2]} {item[3]} {item[4]} {item[5]} is broken"
                )

    return res


def get_clothes_exp(limit, tier):
    setup = [ItemType.al, ItemType.am, ItemType.hm,
             ItemType.hl, ItemType.gl, ItemType.bl]
    get_merchant_exp(limit, setup, tier)
