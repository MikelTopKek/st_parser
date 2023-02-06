import datetime
import os

from src.data_creation import get_section_item
from src.database_requests import best_blue_seven_plus_items_list, worker_exp_request
from src.models import ItemType
from src.settings import guild_bonus_craft_speed
from src.utils import format_number, all_workers_bonus_speed


def get_best_blue_seven_items(limit: int) -> list:
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


def get_optimal_items(max_cost_of_1m_exp: int = 1e3, min_airship_power: int = 0, additional_limit=0,
                      tier: int = 0, min_exp: int = 0):
    print('Filtering optimal items due to env params...')
    # Elements
    get_section_item("Elements", min_exp, 10 + additional_limit,
                     tier, [ItemType.z], max_cost_of_1m_exp,
                     min_airship_power,
                     )
    # Breastplates
    get_section_item(
        "Breastplates",
        min_exp * 1.2,
        3 + additional_limit,
        tier,
        [ItemType.ah, ItemType.am, ItemType.al],
        max_cost_of_1m_exp,
        min_airship_power,
    )
    # Helmets
    get_section_item(
        "Helmets",
        min_exp * 1.5,
        3 + additional_limit,
        tier,
        [ItemType.hh, ItemType.hm, ItemType.hl, ItemType.xc],
        max_cost_of_1m_exp,
        min_airship_power,
    )
    # Weapons (on rack)
    get_section_item(
        "Weapons on rack",
        min_exp * 1.5,
        3 + additional_limit,
        tier,
        [ItemType.ws, ItemType.wa, ItemType.wm, ItemType.wp, ItemType.wt],
        max_cost_of_1m_exp,
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
        max_cost_of_1m_exp,
        min_airship_power,
    )
    # Misc. armor
    get_section_item(
        "Misc armor",
        min_exp,
        5 + additional_limit,
        tier,
        [ItemType.gh, ItemType.gl, ItemType.bh, ItemType.bl],
        max_cost_of_1m_exp,
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
        max_cost_of_1m_exp,
        min_airship_power,
    )


def get_best_airship_item(additional_limit: int, min_airship_power: int, tier: int) -> None:
    get_optimal_items(
        additional_limit=additional_limit,
        min_airship_power=min_airship_power,
        tier=tier,
    )


def get_worker_exp(limit: int, setup: list[ItemType], tier: int):
    res = worker_exp_request(limit, setup, tier)
    with open(os.getenv("OUTPUT_FILENAME"), "a") as file:
        file.write(
            f'Type{"":.<12}| Tier{"":.<0}| Item{"":.<21}| Exp{"":.<7}| '
            f'Worker1{"":.<3}| Worker2{"":.<3}| Worker3{"":.<3}| Crafting_time| Index(exp/h)|\n'
        )
        for item in res:
            number_of_workers = 1
            if item[5] != 'Empty':
                number_of_workers += 1
            if item[6] != 'Empty':
                number_of_workers += 1
            time_in_seconds = round(item[7] *
                                    all_workers_bonus_speed(item[4], item[5], item[6]) * guild_bonus_craft_speed, 0)
            item_time = datetime.timedelta(
                seconds=time_in_seconds
            )
            try:
                experience = round(item[3] / number_of_workers, 1)
                experience_print = format_number(experience)
                # if round(experience/time_in_seconds*3600, 2) < 600 or item[2] < 4:
                #     continue
                file.write(
                    f"{item[1].value:.<16}| {item[2]:.<4}| {item[0]:.<25}| "
                    f"{experience_print:.<10}| {item[4]:.<10}| {str(item[5]):.<10}|"
                    f" {str(item[6]):.<10}| {str(item_time):.<13}| {round(experience / time_in_seconds * 3600, 2):.<12}|\n"
                )
            except Exception as e:
                file.write(
                    f"{str(e)}----Item {item[0]} {item[1]} {item[2]} {item[3]} {item[4]} {item[5]} {item[6]}is broken\n"
                )

    return res


def get_clothes_exp(limit: int, tier: int) -> None:
    setup = [ItemType.al, ItemType.am, ItemType.hm,
             ItemType.hl, ItemType.gl, ItemType.bl]
    get_worker_exp(limit + 10, setup, tier)


def get_meal_exp(limit: int, tier: int) -> None:
    setup = [ItemType.fm]
    get_worker_exp(limit, setup, tier)
