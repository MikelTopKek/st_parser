import sqlalchemy as sa
from sqlalchemy import Float, case, cast

from src.models import Item, ItemQuality, ItemType, MarketStats
from src.settings import engine

item_table = Item.__table__
market_stats = MarketStats.__table__


def recent_date() -> str:
    """Send request and get recent trading date .

    Returns:
        str: datetime
    """
    return engine.execute(
        sa.select(
            [market_stats.c.created_at]).select_from(market_stats).order_by(
                market_stats.c.created_at.desc()).limit(1)).fetchall()[0][0]


def best_blue_seven_plus_items_list(limit: int) -> list:
    """Send request to db and get of the best items with 7+ tier and quality greater or equal to flawless.

    Args:
        limit (int): more limit -> more results displayed

    Returns:
        list: response with results
    """
    return engine.execute(
        sa.select([
            item_table.c.name,
            item_table.c.item_type,
            item_table.c.tier,
            market_stats.c.quality,
            market_stats.c.gold_price,
            market_stats.c.created_at,
        ]).select_from(
            item_table.join(
                market_stats,
                item_table.c.uid == market_stats.c.item_id)).filter(
                    sa.and_(
                        market_stats.c.created_at == recent_date(),
                        market_stats.c.gold_price > 0,
                        item_table.c.tier >= 7,
                        market_stats.c.quality != ItemQuality.common,
                        market_stats.c.quality != ItemQuality.uncommon,
                    )).order_by(
                        market_stats.c.gold_price).limit(limit)).fetchall()


def items_list(min_exp: float, limit: int, tier: int, setup: list[ItemType],
               min_airship_power: int, max_cost_of_1m_exp: int) -> list:
    """Send request and get a list of items in the market .

    Args:
        min_exp (float): item minimum experience
        limit (int): more limit -> more results displayed
        tier (int): items with less than or equal to tier will be displayed in the result
        setup (list[ItemType]):  list of item types which request used to get items
        min_airship_power (int):  min airship power to display items with best airship power
            (if 0 - display best items to levelling)
        max_cost_of_1m_exp (int):  max cost of 1 million experience in millions gold. Defaults to 1_000.

    Returns:
        list: response with results
    """
    if min_airship_power == 0:
        sql_req = (
            sa.select([
                item_table.c.name,
                item_table.c.item_type,
                item_table.c.tier,
                item_table.c.merchant_exp,
                market_stats.c.quality,
                market_stats.c.gold_price,
                market_stats.c.created_at,
                item_table.c.airship_power,
                item_table.c.base_gold_value,
            ]).select_from(
                item_table.join(
                    market_stats,
                    item_table.c.uid == market_stats.c.item_id)).filter(
                        sa.and_(
                            market_stats.c.created_at == recent_date(),
                            market_stats.c.gold_price > 0,
                            item_table.c.item_type.in_(setup),
                            item_table.c.tier <= tier,
                            cast(
                                market_stats.c.gold_price -
                                item_table.c.base_gold_value, Float) /
                            cast(item_table.c.merchant_exp, Float) <= cast(
                                max_cost_of_1m_exp, Float),
                            item_table.c.airship_power > min_airship_power,
                            item_table.c.merchant_exp > min_exp)).
            order_by(
                # item_table.c.merchant_exp,
                cast(market_stats.c.gold_price - item_table.c.base_gold_value,
                     Float) /
                cast(item_table.c.merchant_exp, Float), ).limit(limit))

        res = engine.execute(sql_req).fetchall()

        return res

    return engine.execute(
        sa.select([
            item_table.c.name,
            item_table.c.item_type,
            item_table.c.tier,
            item_table.c.merchant_exp,
            market_stats.c.quality,
            market_stats.c.gold_price,
            market_stats.c.created_at,
            item_table.c.airship_power,
            item_table.c.base_gold_value,
        ]).select_from(
            item_table.join(market_stats,
                            item_table.c.uid == market_stats.c.item_id)).
        filter(
            sa.and_(
                market_stats.c.created_at == recent_date(),
                market_stats.c.gold_price > 0,
                item_table.c.item_type.in_(setup),
                item_table.c.tier <= tier,
                (market_stats.c.gold_price - item_table.c.base_gold_value) /
                item_table.c.merchant_exp * 1.0 <= max_cost_of_1m_exp,
                item_table.c.airship_power > min_airship_power,
                item_table.c.item_type != ItemType.xf,
            )).order_by(
                item_table.c.airship_power.desc(), ).limit(limit)).fetchall()


def worker_exp_request(limit: int, setup: list[ItemType], tier: int) -> list:
    """Send request to db and get items with higher worker experience.

    Args:
        limit (int): more limit -> more results displayed
        setup (list[ItemType]): list of item types which request used to get items
        tier (int): items with less than or equal to tier will be displayed in the result

    Returns:
        list: response with results
    """
    return engine.execute(
        sa.select([
            item_table.c.name, item_table.c.item_type, item_table.c.tier,
            item_table.c.worker_exp, item_table.c.worker1,
            item_table.c.worker2, item_table.c.worker3,
            item_table.c.base_crafting_time, item_table.c.receipt_availability
        ]).select_from(item_table).filter(
            sa.and_(item_table.c.item_type.in_(setup),
                    item_table.c.tier <= tier,
                    item_table.c.receipt_availability == 'True')).order_by(
                        item_table.c.base_crafting_time /
                        item_table.c.worker_exp).limit(limit + 10)).fetchall()


def best_crafting_items(limit: int, tier: int, min_tier: int) -> list:
    """Send request to db and get bestcrafting items which have best ratio highest price on market and lowest time
        to craft.

    Args:
        limit (int): more limit -> more results displayed
        tier (int): items with less than or equal to tier will be displayed in the result
        min_tier (int): items with greater than or equal to tier will be displayed in the result

    Returns:
        list: response with results
    """
    return engine.execute(
        sa.select([
            item_table.c.name, item_table.c.item_type, item_table.c.tier,
            item_table.c.base_gold_value, item_table.c.worker1,
            item_table.c.worker2, item_table.c.worker3,
            item_table.c.base_crafting_time, market_stats.c.gold_price,
            market_stats.c.created_at, market_stats.c.quality,
            item_table.c.receipt_availability, market_stats.c.gold_qty
        ]).select_from(
            item_table.join(
                market_stats,
                item_table.c.uid == market_stats.c.item_id)).filter(
                    sa.and_(
                        market_stats.c.created_at == recent_date(),
                        item_table.c.tier <= tier,
                        item_table.c.tier >= min_tier,
                        market_stats.c.quality == ItemQuality.common,
                        item_table.c.receipt_availability == 'True',
                    )).order_by(
                        case([
                            (
                                market_stats.c.gold_price > 0,
                                market_stats.c.gold_price /
                                item_table.c.base_crafting_time,
                            ),
                            (market_stats.c.gold_price == 0,
                             item_table.c.base_gold_value * 10 /
                             item_table.c.base_crafting_time),
                        ]).desc()).limit(limit)).fetchall()


def items_with_blueprints() -> list:
    """Send request to db and get all items with blueprints availability.

    Returns:
        list: response with results
    """
    return engine.execute(
        sa.select([
            item_table.c.name, item_table.c.item_type, item_table.c.tier,
            item_table.c.uid, item_table.c.receipt_availability
        ]).select_from(item_table).order_by(item_table.c.item_type,
                                            item_table.c.tier)).fetchall()


def get_item(item_uid: str, quality: ItemQuality = ItemQuality.common) -> list:
    """Send request to db and get exact item due to params.

    Args:
        item_uid (str): item unique uid
        quality (ItemQuality, optional): item quality on sale in market. Defaults to ItemQuality.common.

    Returns:
        list: response with results
    """
    return engine.execute(
        sa.select([
            item_table.c.uid,
            market_stats.c.gold_price,
            market_stats.c.quality,
            item_table.c.item_type,
        ]).select_from(
            item_table.join(
                market_stats,
                item_table.c.uid == market_stats.c.item_id)).filter(
                    item_table.c.uid == item_uid,
                    market_stats.c.quality == quality)).first()
