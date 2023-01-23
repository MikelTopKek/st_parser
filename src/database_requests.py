import sqlalchemy as sa
from sqlalchemy import case

from src.models import ItemQuality, ItemType
from src.settings import engine, item_table, market_stats


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
        .limit(limit + 10)
    ).fetchall()


def items_list(name, exp, limit, tier, setup, min_airship_power):
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
                        market_stats.c.gold_price /
                        item_table.c.merchant_exp * (-1),
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
            ).desc()
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
                item_table.c.base_crafting_time
            ]
        )
        .select_from(
            item_table
        )
        .filter(
            sa.and_(
                item_table.c.item_type.in_(setup),
                item_table.c.tier <= tier

            )
        )
        .order_by(
            case(
                [
                    (
                        item_table.c.worker2 != 'Empty' and item_table.c.worker3 != 'Empty',
                        item_table.c.worker_exp / 3
                    ),
                    (
                        item_table.c.worker2 != 'Empty' and item_table.c.worker3 == 'Empty',
                        item_table.c.worker_exp / 2
                    ),
                    (
                        item_table.c.worker2 == 'Empty' and item_table.c.worker3 == 'Empty',
                        item_table.c.worker_exp,
                    ),
                ]
            ).desc()
        )
        .limit(limit + 30)
    ).fetchall()
