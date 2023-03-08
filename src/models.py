import enum
from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, Enum, Float, ForeignKey,
                        Integer, MetaData, String)
from sqlalchemy.orm import declarative_base

metadata = MetaData()
ModelBase = declarative_base(metadata=metadata)


class ItemType(enum.Enum):
    """Returns a class representing the item type.
    """
    ws = "sword"
    wa = "axe"
    wd = "dagger"
    wm = "mace"
    wp = "spear"
    wb = "bow"
    wt = "staff"
    ww = "wand"
    wg = "gun"
    wc = "crossbow"
    ah = "heavy_armor"
    am = "light_armor"
    al = "clothes"
    hh = "helmet"
    hm = "rogue_hat"
    hl = "magician_hat"
    gh = "gauntlets"
    gl = "gloves"
    bh = "heavy_footwear"
    bl = "light_footwear"
    uh = "herbal_medicine"
    up = "potion"
    us = "spell"
    xs = "shield"
    xr = "ring"
    xa = "amulet"
    xc = "cloak"
    xf = "familiar"
    fm = "meal"
    fd = "dessert"
    z = "element/spirit"
    m = "other"

    xu = "etc"
    xm = "etc2"


class ItemQuality(enum.Enum):
    """Returns a class representing the item quality .
    """
    legendary = "legendary"
    epic = "epic"
    uncommon = "uncommon"
    flawless = "flawless"
    common = "common"


class MarketStats(ModelBase):
    """Class with a table contains items which are currently on sale .
    """
    __tablename__ = "marketstats"

    id: int = Column(Integer, primary_key=True)
    item_id: str = Column(String, ForeignKey("item.uid"))
    quality: ItemQuality = Column(Enum(ItemQuality))
    gold_price: int = Column(Integer)
    gold_qty: int = Column(Integer)
    gems_price: int = Column(Integer)
    gems_qty: int = Column(Integer)
    received_at: datetime = Column(DateTime)
    created_at: datetime = Column(DateTime, default=datetime.utcnow())


class Item(ModelBase):  # pylint: disable=too-few-public-methods
    """Class with a table contains items details .
    """
    __tablename__ = "item"

    uid: str = Column(String, primary_key=True)
    item_type: ItemType = Column(Enum(ItemType))
    name: str = Column(String)
    tier: int = Column(Integer)
    image: str = Column(String)
    base_gold_value: int = Column(Integer)
    merchant_exp: int = Column(Integer)
    worker_exp: int = Column(Integer)
    worker1: str = Column(String)
    worker2: str = Column(String)
    worker3: str = Column(String)
    favor: int = Column(Integer)
    airship_power: int = Column(Integer)
    collection_score: int = Column(Integer)
    energy_score: int = Column(Integer)
    energy_cost: int = Column(Integer)
    base_crafting_time: int = Column(Integer)
    bonus_crafting_time: float = Column(Float)
    receipt_availability: bool = Column(Boolean, default=False)
