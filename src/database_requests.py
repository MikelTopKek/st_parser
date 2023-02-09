import sqlalchemy as sa
from sqlalchemy import case

from src.models import ItemQuality, ItemType
from src.settings import engine, item_table, market_stats
from src.utils import all_workers_bonus_speed


def recent_date():
    conn = engine
    return conn.execute(
        sa.select([market_stats.c.created_at])
        .select_from(market_stats)
        .order_by(market_stats.c.created_at.desc())
        .limit(1)
    ).fetchall()[0][0]


def best_blue_seven_plus_items_list(limit):
    conn = engine
    return conn.execute(
        sa.select(
            [
                item_table.c.name,
                item_table.c.item_type,
                item_table.c.tier,
                market_stats.c.quality,
                market_stats.c.gold_price,
                market_stats.c.created_at,
            ]
        )
        .select_from(
            item_table.join(market_stats, item_table.c.uid ==
                            market_stats.c.item_id)
        )
        .filter(
            sa.and_(
                market_stats.c.created_at == recent_date(),
                market_stats.c.gold_price > 0,
                item_table.c.tier >= 7,
                market_stats.c.quality != ItemQuality.common,
                market_stats.c.quality != ItemQuality.uncommon,
            )
        )
        .order_by(market_stats.c.gold_price)
        .limit(limit)
    ).fetchall()


def items_list(exp, limit, tier, setup, min_airship_power, max_cost_of_1m_exp):
    conn = engine
    return conn.execute(
        sa.select(
            [
                item_table.c.name,
                item_table.c.item_type,
                item_table.c.tier,
                item_table.c.merchant_exp,
                market_stats.c.quality,
                market_stats.c.gold_price,
                market_stats.c.created_at,
                item_table.c.airship_power,
                item_table.c.base_gold_value,
            ]
        )
        .select_from(
            item_table.join(market_stats, item_table.c.uid ==
                            market_stats.c.item_id)
        )
        .filter(
            sa.and_(
                market_stats.c.created_at == recent_date(),
                market_stats.c.gold_price > 0,
                item_table.c.item_type.in_(setup),
                item_table.c.tier <= tier,
                (market_stats.c.gold_price - item_table.c.base_gold_value) /
                item_table.c.merchant_exp <= max_cost_of_1m_exp,
                item_table.c.airship_power > min_airship_power,
                case(
                    [
                        (min_airship_power != 0,
                         item_table.c.item_type != ItemType.xf),
                        (min_airship_power == 0, item_table.c.merchant_exp > exp),
                    ]
                ),
            )
        )
        .order_by(
            case(
                [
                    (
                        min_airship_power == 0,
                        (market_stats.c.gold_price - item_table.c.base_gold_value) /
                        item_table.c.merchant_exp,
                    ),
                    (
                        min_airship_power != 0,
                        case(
                            (
                                market_stats.c.quality == ItemQuality.uncommon,
                                item_table.c.airship_power * 1.25,
                            ),
                            (
                                market_stats.c.quality == ItemQuality.flawless,
                                item_table.c.airship_power * 1.5,
                            ),
                            (
                                market_stats.c.quality == ItemQuality.epic,
                                item_table.c.airship_power * 2,
                            ),
                            (
                                market_stats.c.quality == ItemQuality.legendary,
                                item_table.c.airship_power * 3,
                            ),
                            (
                                market_stats.c.quality == ItemQuality.common,
                                item_table.c.airship_power,
                            ),
                        ),
                    ),
                ]
            )
        )
        .limit(limit)
    ).fetchall()


def worker_exp_request(limit, setup, tier):

    conn = engine
    return conn.execute(
        sa.select(
            [
                item_table.c.name,
                item_table.c.item_type,
                item_table.c.tier,
                item_table.c.worker_exp,
                item_table.c.worker1,
                item_table.c.worker2,
                item_table.c.worker3,
                item_table.c.base_crafting_time,
                item_table.c.receipt_availability
            ]
        )
        .select_from(
            item_table
        )
        .filter(
            sa.and_(
                item_table.c.item_type.in_(setup),
                item_table.c.tier <= tier,
                item_table.c.receipt_availability == 'True'

            )
        )
        .order_by(
            (item_table.c.base_crafting_time/all_workers_bonus_speed(item_table.c.worker1,
                                                                     item_table.c.worker2,
                                                                     item_table.c.worker3)).desc()
        )
        .limit(limit + 10)
    ).fetchall()


def best_crafting_items(limit, tier, min_tier):
    conn = engine
    return conn.execute(
        sa.select(
            [
                item_table.c.name,
                item_table.c.item_type,
                item_table.c.tier,
                item_table.c.base_gold_value,
                item_table.c.worker1,
                item_table.c.worker2,
                item_table.c.worker3,
                item_table.c.base_crafting_time,
                market_stats.c.gold_price,
                market_stats.c.created_at,
                market_stats.c.quality,
                item_table.c.receipt_availability,
                market_stats.c.gold_qty
            ]
        )
        .select_from(
            item_table.join(market_stats, item_table.c.uid ==
                            market_stats.c.item_id)
        )
        .filter(
            sa.and_(
                market_stats.c.created_at == recent_date(),
                item_table.c.tier <= tier,
                item_table.c.tier >= min_tier,
                market_stats.c.quality == ItemQuality.common,
                item_table.c.receipt_availability == 'True',
            )
        )
        .order_by(
            case(
                [
                    (
                        market_stats.c.gold_price > 0,
                        market_stats.c.gold_price / item_table.c.base_crafting_time,
                    ),
                    (
                        market_stats.c.gold_price == 0,
                        item_table.c.base_gold_value * 10 / item_table.c.base_crafting_time

                    ),
                ]
            ).desc()
        )
        .limit(limit)
    ).fetchall()


def items_with_blueprints():

    conn = engine
    return conn.execute(
        sa.select(
            [
                item_table.c.name,
                item_table.c.item_type,
                item_table.c.tier,
                item_table.c.uid,
                item_table.c.receipt_availability
            ]
        )
        .select_from(
            item_table
        )
        .order_by(
            item_table.c.item_type,
            item_table.c.tier
        )
    ).fetchall()


def get_item(item_uid, quality=ItemQuality.common):
    conn = engine

    return conn.execute(
        sa.select(
            [
                item_table.c.uid,
                market_stats.c.gold_price,
                market_stats.c.quality,
                item_table.c.item_type,

            ]
        )
        .select_from(
            item_table.join(market_stats, item_table.c.uid ==
                            market_stats.c.item_id)
        )
        .filter(
            item_table.c.uid == item_uid,
            market_stats.c.quality == quality

        )
    ).first()
