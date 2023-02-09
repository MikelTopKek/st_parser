import datetime
import os

from src.data_creation import get_section_item
from src.database_requests import best_blue_seven_plus_items_list, worker_exp_request, best_crafting_items, get_item
from src.models import ItemType
from src.settings import guild_bonus_craft_speed, SOLD_PER_HOUR, NEEDED_EXP, NUMBER_OF_CRAFT_SLOTS
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
    elements_avg = get_section_item("Elements", min_exp, 10 + additional_limit,
                     tier, [ItemType.z], max_cost_of_1m_exp,
                     min_airship_power,
                     )
    # Breastplates
    brestpates_avg = get_section_item(
        "Breastplates",
        min_exp * 1.2,
        3 + additional_limit,
        tier,
        [ItemType.ah, ItemType.am, ItemType.al],
        max_cost_of_1m_exp,
        min_airship_power,
    )
    # Helmets
    helmets_avg = get_section_item(
        "Helmets",
        min_exp * 1.5,
        3 + additional_limit,
        tier,
        [ItemType.hh, ItemType.hm, ItemType.hl, ItemType.xc],
        max_cost_of_1m_exp,
        min_airship_power,
    )
    # Weapons (on rack)
    weapons_rack_avg = get_section_item(
        "Weapons on rack",
        min_exp * 1.5,
        3 + additional_limit,
        tier,
        [ItemType.ws, ItemType.wa, ItemType.wm, ItemType.wp, ItemType.wt],
        max_cost_of_1m_exp,
        min_airship_power,
    )
    # Weapons (on table)
    weapons_table_avg = get_section_item(
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
    misc_armor_avg = get_section_item(
        "Misc armor",
        min_exp,
        5 + additional_limit,
        tier,
        [ItemType.gh, ItemType.gl, ItemType.bh, ItemType.bl],
        max_cost_of_1m_exp,
        min_airship_power,
    )
    # Accessories
    accesoires_avg = get_section_item(
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
    avg_1m_exp_cost: float = (accesoires_avg[0] + helmets_avg[0] + elements_avg[0] + brestpates_avg[0]
                              + misc_armor_avg[0] + weapons_rack_avg[0] + weapons_table_avg[0]) / 7  # in millions
    sold_per_hour: int = SOLD_PER_HOUR
    avg_exp_per_item: float = (accesoires_avg[1] + helmets_avg[1] + elements_avg[1] + brestpates_avg[1]
                               + misc_armor_avg[1] + weapons_rack_avg[1] + weapons_table_avg[1]) / 7  # in millions
    experience: int = NEEDED_EXP  # in millions, how much exp need to get

    number_of_items: float = experience * 1_000_000 / avg_exp_per_item

    gold_required: float = experience * avg_1m_exp_cost  # in millions, how much gold we need to up

    hours_to_sell_items: float = number_of_items / sold_per_hour  # Time to spend to sell all items

    print(f'Exp needed: {experience} millions, sold per hour = {sold_per_hour}.\n'
          f'AVG item experience: {format_number(avg_exp_per_item)} exp, '
          f'avg 1m experience cost: {format_number(avg_1m_exp_cost)}m.\n'
          f'Need {format_number(number_of_items)} items.\n'
          f'Gold we need to sell items on {format_number(gold_required)}\n'
          f'Time to spend to sell all items: {format_number(hours_to_sell_items)} hours.')


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


def cheapest_sigil(limit):
    blue_res = get_best_blue_seven_items(limit=limit)
    blue_items_avg_cost = 0

    for item in blue_res:
        try:
            blue_items_avg_cost += item[4]
        except Exception as e:
            print(f"{str(e)}; Item {item[0]} {item[1]} {item[2]} {item[3]} {item[4]} {item[5]} is broken\n")

    blue_items_avg_cost /= limit

    moonstone_cost = get_item('greatermoon')[1]
    obsidian_cost = get_item('obsidian')[1]
    magmacore_cost = get_item('magmacore')[1]
    crabclaw_cost = get_item('crabclaw')[1]
    blue_sigil_cost = get_item('sparksigil2')[1]
    red_sigil_cost = get_item('mightsigil2')[1]
    green_sigil_cost = get_item('gracesigil2')[1]

    sigil_time_index: float = 60 / 53

    def sigil_profit(name: str, market_cost: float, material_cost: float) -> str:
        from src.utils import sigil_craft_cost
        sigil_craft_cost = sigil_craft_cost(blue_items_avg_cost=blue_items_avg_cost,
                                            moonstone_cost=moonstone_cost,
                                            material_cost=material_cost)

        profit_index = (market_cost * 0.9 * 4 - sigil_craft_cost) * sigil_time_index / 1_000_000
        profit = format_number(profit_index * NUMBER_OF_CRAFT_SLOTS)
        return f'{name} sigil costs {profit} per {NUMBER_OF_CRAFT_SLOTS} slots ' \
               f'because of material cost: {format_number(material_cost)}.| Profit_index: {format_number(profit_index)}'

    blue_sigil_craft_cost = sigil_profit(name='Blue', market_cost=blue_sigil_cost, material_cost=magmacore_cost)
    red_sigil_craft_cost = sigil_profit(name='Red', market_cost=red_sigil_cost, material_cost=crabclaw_cost)
    green_sigil_craft_cost = sigil_profit(name='Green', market_cost=green_sigil_cost, material_cost=obsidian_cost)

    return f"{blue_sigil_craft_cost}\n" \
           f"{red_sigil_craft_cost}\n" \
           f"{green_sigil_craft_cost}\n"


def get_best_crafting_items(limit: int, tier: int, min_tier: int) -> None:
    res = best_crafting_items(limit=limit * 3, tier=tier, min_tier=min_tier)

    with open(os.getenv("OUTPUT_FILENAME"), "a") as file:
        file.write(cheapest_sigil(limit=round(limit / 2, 0)))

        file.write(
            f'Type{"":.<12}| Tier{"":.<0}| Name{"":.<21}| '
            f'Market value| Base gold value| Quantity_gold| Crafting time| Index(millions gold/h)|\n'
        )

        for item in res:

            time_in_minutes = round(item[7] *
                                    all_workers_bonus_speed(item[4], item[5], item[6])
                                    * guild_bonus_craft_speed, 0) / 60
            item_time = datetime.timedelta(
                minutes=time_in_minutes
            )
            try:
                # if round(gold_value / time_in_minutes * 60 / 1_000_000, 2) > 1:
                if item[8] > 0:
                    gold_value = item[8]
                    is_only_crystal = 'For gold'
                else:
                    gold_value = item[3] * 10
                    is_only_crystal = 'Only crystal'

                file.write(
                    f"{item[1].value:.<16}| {item[2]:.<4}| {item[0]:.<25}| {format_number(gold_value):.<12}| "
                    f"{format_number(item[3]):.<15}| {item[12]:.<13}| {str(item_time):.<13}| "
                    f"{round(gold_value / time_in_minutes * 60 / 1_000_000, 2):.<22}| {is_only_crystal}\n"
                )

            except Exception as e:
                file.write(
                    f"{str(e)}----Item {item[0]} {item[1]} {item[2]} {item[3]} {item[4]} {item[5]} {item[6]}is broken\n"
                )
