import datetime
import logging.config

from src.data_creation import get_section_item
from src.database_requests import (best_blue_seven_plus_items_list,
                                   best_crafting_items, get_item,
                                   worker_exp_request)
from src.models import ItemType
from src.settings import (LOGGING, NEEDED_EXP, NUMBER_OF_CRAFT_SLOTS,
                          SOLD_PER_HOUR, guild_bonus_craft_speed)
from src.utils import all_workers_bonus_speed, format_number, sigil_craft_cost

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('main_logger')
error_logger = logging.getLogger('error_logger')


def get_best_blue_seven_items(limit: int) -> list:
    """Get a list of the best items with 7+ tier and quality greater or equal to flawless.

    Args:
        limit (int): more limit -> more results displayed

    Returns:
        list: list of items
    """
    res = best_blue_seven_plus_items_list(limit)

    logger.info(f'Type{"":.<12}| Tier{"":.<0}| Item{"":.<21}| Quality{"":.<3}| Gold{"":.<6}|')
    for item in res:
        try:
            gold_value = format_number(item[4])
            logger.info(
                f"{item[1].value:.<16}| {item[2]:.<4}| {item[0]:.<25}| "
                f"{item[3].value:.<10}| {gold_value:.<10}|"
            )
        except KeyError:
            error_logger.error(
                f"Item {item[0]} {item[1]} {item[2]} {item[3]} {item[4]} {item[5]} is broken"
            )

    return res


def get_optimal_items(max_cost_of_1m_exp: int = 1_000, min_airship_power: int = 0, additional_limit: int = 0,
                      tier: int = 0, min_exp: int = 0) -> None:
    """Get a list of optimal items for the cheapest levelling .

    Args:
        max_cost_of_1m_exp (int, optional): max cost of 1 million experience in millions gold. Defaults to 1_000.
        min_airship_power (int, optional): min airship power to display items with best airship power
            (if 0 - display best items to levelling). Defaults to 0.
        additional_limit (int, optional):  more limit -> more results displayed. Defaults to 0.
        tier (int, optional): items with less than or equal to tier will be displayed in the result. Defaults to 0.
        min_exp (int, optional): items with less than or equal experience will be displayed in the result. Defaults 0.
    """
    logger.info('Filtering optimal items due to env params...')

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
    avg_exp_per_item: float = (accesoires_avg[1] + helmets_avg[1] + elements_avg[1] + brestpates_avg[1]
                               + misc_armor_avg[1] + weapons_rack_avg[1] + weapons_table_avg[1]) / 7  # in millions
    experience: int = NEEDED_EXP  # in millions, how much exp need to get

    number_of_items: float = experience * 1_000_000 / avg_exp_per_item if avg_exp_per_item > 0 else 0

    gold_required: float = experience * avg_1m_exp_cost  # in millions, how much gold we need to up

    hours_to_sell_items: float = number_of_items / SOLD_PER_HOUR  # Time to spend to sell all items
    if min_airship_power == 0:
        logger.info(f'Exp needed: {experience} millions, sold per hour = {SOLD_PER_HOUR}.\n'
                    f'AVG item experience: {format_number(avg_exp_per_item)} exp, '
                    f'avg 1m experience cost: {format_number(avg_1m_exp_cost)}m.\n'
                    f'Need {format_number(number_of_items)} items.\n'
                    f'Gold we need to sell items on {format_number(gold_required)}.\n'
                    f'Time to spend to sell all items: {format_number(hours_to_sell_items)} hours.')


def get_best_airship_item(additional_limit: int, min_airship_power: int, tier: int) -> None:
    """Get the best items with the highest airship power.

    Args:
        additional_limit (int): more limit -> more results displayed
        min_airship_power (int): items with more power than the minimum power will be displayed in the result
        tier (int): items with less than or equal to tier will be displayed in the result
    """
    get_optimal_items(
        additional_limit=additional_limit,
        min_airship_power=min_airship_power,
        tier=tier,
    )


def get_worker_exp(limit: int, setup: list[ItemType], tier: int) -> list:
    """Get worker exp rate .

    Args:
        limit (int): more limit -> more results displayed
        setup (list[ItemType]): list of item types which request used to get items
        tier (int): items with less than or equal to tier will be displayed in the result
    """
    res = worker_exp_request(limit=limit, setup=setup, tier=tier)

    logger.info(
        f'Type{"":.<12}| Tier{"":.<0}| Item{"":.<21}| Exp{"":.<7}| '
        f'Worker1{"":.<3}| Worker2{"":.<3}| Worker3{"":.<3}| Crafting_time| Index(exp/h)|'
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

            logger.info(
                f"{item[1].value:.<16}| {item[2]:.<4}| {item[0]:.<25}| "
                f"{experience_print:.<10}| {item[4]:.<10}| {str(item[5]):.<10}|"
                f" {str(item[6]):.<10}| {str(item_time):.<13}| {round(experience / time_in_seconds * 3600, 2):.<12}|"
            )

        except KeyError as e:
            error_logger.error(
                f"{str(e)}----Item {item[0]} {item[1]} {item[2]} {item[3]} {item[4]} {item[5]} {item[6]}is broken"
            )


def get_clothes_exp(limit: int, tier: int) -> None:
    """Get best clothes with best experience rate to up worker level.

    Args:
        limit (int): more limit -> more results displayed
        tier (int): items with less than or equal to tier will be displayed in the result
    """
    setup = [ItemType.al, ItemType.am, ItemType.hm,
             ItemType.hl, ItemType.gl, ItemType.bl]
    get_worker_exp(limit=limit + 10, setup=setup, tier=tier)


def get_meal_exp(limit: int, tier: int) -> None:
    """Get best meals with best experience rate to up worker level.

    Args:
        limit (int): more limit -> more results displayed
        tier (int): items with less than or equal to tier will be displayed in the result
    """
    setup = [ItemType.fm]
    get_worker_exp(limit=limit, setup=setup, tier=tier)

def sigil_profit(name: str, market_cost: float, material_cost: float,
                 blue_items_avg_cost: float, moonstone_cost: float, sigil_time_index: float) -> str:
    """Generate a sigil profit .

    Args:
        name (str): sigil`s name
        market_cost (float): market price of sigil`s
        material_cost (float): cost of all materials to craft
        blue_items_avg_cost (float): average cost of flawless items to craft
        moonstone_cost (float): market price of moonstones
        sigil_time_index (float): index, increase profit_index of sigil by crafting time (53 minutes -> index=60/53)

    Returns:
        str: info about certain sigil profit
    """
    sigil_cost = sigil_craft_cost(blue_items_avg_cost=blue_items_avg_cost,
                                  moonstone_cost=moonstone_cost,
                                  material_cost=material_cost)

    profit_index = (market_cost * 0.9 * 4 - sigil_cost) * sigil_time_index / 1_000_000
    profit = format_number(profit_index * NUMBER_OF_CRAFT_SLOTS)
    return f'{name} sigil costs {profit} per {NUMBER_OF_CRAFT_SLOTS} slots ' \
            f'because of material cost: {format_number(material_cost)}.| Profit_index: {format_number(profit_index)}'

def cheapest_sigil(limit: int) -> str:
    """Calculates the cheapest price for a sigils.

    Args:
        limit (int): more limit -> more results displayed

    Returns:
        str: info about all sigils
    """
    blue_res = get_best_blue_seven_items(limit=limit)
    blue_items_avg_cost: float = 0

    for item in blue_res:
        try:
            blue_items_avg_cost += item[4]
        except KeyError as e:
            error_logger.error(f"{str(e)}; Item {item[0]} {item[1]} {item[2]} {item[3]} {item[4]} {item[5]} is broken")

    blue_items_avg_cost /= limit

    moonstone_cost: int = get_item('greatermoon')[1]
    obsidian_cost: int = get_item('obsidian')[1]
    magmacore_cost: int = get_item('magmacore')[1]
    crabclaw_cost: int = get_item('crabclaw')[1]
    blue_sigil_cost: int = get_item('sparksigil2')[1]
    red_sigil_cost: int = get_item('mightsigil2')[1]
    green_sigil_cost: int = get_item('gracesigil2')[1]

    sigil_time_index: float = 60 / 53

    blue_sigil_craft_cost = sigil_profit(name='Blue', market_cost=blue_sigil_cost, material_cost=magmacore_cost,
                                         blue_items_avg_cost=blue_items_avg_cost, moonstone_cost=moonstone_cost,
                                         sigil_time_index=sigil_time_index)
    red_sigil_craft_cost = sigil_profit(name='Red', market_cost=red_sigil_cost, material_cost=crabclaw_cost,
                                         blue_items_avg_cost=blue_items_avg_cost, moonstone_cost=moonstone_cost,
                                         sigil_time_index=sigil_time_index)
    green_sigil_craft_cost = sigil_profit(name='Green', market_cost=green_sigil_cost, material_cost=obsidian_cost,
                                         blue_items_avg_cost=blue_items_avg_cost, moonstone_cost=moonstone_cost,
                                         sigil_time_index=sigil_time_index)

    return f"Sigils:\n" \
           f"{blue_sigil_craft_cost}\n" \
           f"{red_sigil_craft_cost}\n" \
           f"{green_sigil_craft_cost}\n"


def get_best_crafting_items(limit: int, tier: int, min_tier: int) -> None:
    """Get bestcrafting items which have best ratio highest price on market and lowest time to craft.

    Args:
        limit (int): more limit -> more results displayed
        tier (int): items with less than or equal to tier will be displayed in the result
        min_tier (int): items with greater than or equal to tier will be displayed in the result
    """
    res = best_crafting_items(limit=limit * 3, tier=tier, min_tier=min_tier)

    logger.info(cheapest_sigil(limit=round(limit / 2)))

    logger.info(
        f'Type{"":.<12}| Tier{"":.<0}| Name{"":.<21}| '
        f'Market value| Base gold value| Quantity_gold| Crafting time| Index(millions gold/h)|'
    )

    for item in res:

        time_in_minutes = round(item[7] *
                                all_workers_bonus_speed(item[4], item[5], item[6])
                                * guild_bonus_craft_speed, 0) / 60
        item_time = datetime.timedelta(
            minutes=time_in_minutes
        )
        try:
            if item[8] > 0:
                gold_value = item[8]
                is_only_crystal = 'For gold'
            else:
                gold_value = item[3] * 10
                is_only_crystal = 'Only crystal'

            logger.info(
                f"{item[1].value:.<16}| {item[2]:.<4}| {item[0]:.<25}| {format_number(gold_value):.<12}| "
                f"{format_number(item[3]):.<15}| {item[12]:.<13}| {str(item_time):.<13}| "
                f"{round(gold_value / time_in_minutes * 60 / 1_000_000, 2):.<22}| {is_only_crystal}"
            )

        except KeyError as e:
            error_logger.error(
                f"{str(e)}----Item {item[0]} {item[1]} {item[2]} {item[3]} {item[4]} {item[5]} {item[6]}is broken"
            )
