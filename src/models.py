import enum
from dataclasses import dataclass
from typing import List

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, create_engine, Table, MetaData

from sqlalchemy.orm import relationship, sessionmaker

from sqlalchemy.orm import declarative_base

metadata = MetaData()
Base = declarative_base(metadata=metadata)

engine = create_engine('postgresql+psycopg2://postgres:postgres@db:5432/postgres')

Session = sessionmaker(bind=engine)
session = Session()


class ItemClass(enum.Enum):
    weapon = "weapon"
    armor = "armor"
    accessory = "accessory"
    enchantment = "enchantment"
    stone = "stone"
    special_item = "special_item"


class ItemType(enum.Enum):
    sword = "sword"
    axe = "axe"
    dagger = "dagger"
    mace = "mace"
    spear = "spear"
    bow = "bow"
    wand = "wand"
    stave = "stave"
    gun = "gun"
    crossbow = "crossbow"
    heavy_armor = "heavy_armor"
    light_armor = "light_armor"
    clothes = "clothes"
    helmet = "helmet"
    rogue_hat = "rogue_hat"
    magician_hat = "magician_hat"
    gauntlets = "gauntlets"
    gloves = "gloves"
    heavy_footwear = "heavy_footwear"
    light_footwear = "light_footwear"
    herbal_medicine = "herbal_medicine"
    potion = "potion"
    spell = "spell"
    shield = "shield"
    ring = "ring"
    amulet = "amulet"
    cloak = "cloak"
    familiar = "familiar"
    meal = "meal"
    dessert = "dessert"
    runestone = "runestone"
    moonstone = "moonstone"


@dataclass(init=True)
class MarketStats(Base):
    __tablename__ = "marketstats"

    id: int = Column(Integer, primary_key=True)
    item_id: int = Column(Integer, ForeignKey("item.id"))
    gold_price: int = Column(Integer)
    gold_qty: int = Column(Integer)
    gems_price: int = Column(Integer)
    gems_qty: int = Column(Integer)
    received_at: DateTime = Column(DateTime)


@dataclass(init=True)
class Item(Base):
    __tablename__ = "item"

    id: int = Column(Integer, primary_key=True)
    item_class: Enum(ItemClass) = Column(Enum(ItemClass))
    item_type: Enum(ItemType) = Column(Enum(ItemType))
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
    base_crafting_time: str = Column(String)
    marketstats: List["MarketStats"] = relationship("MarketStats")


metadata.create_all(engine)
