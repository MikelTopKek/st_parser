import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, create_engine

from sqlalchemy.orm import relationship, sessionmaker


from sqlalchemy.orm import declarative_base
Base = declarative_base()

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


class Item(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    tier = Column(Integer)
    item_class = Column(Enum(ItemClass))
    item_type = Column(Enum(ItemType))
    image = Column(String)
    base_gold_value = Column(String)
    merchant_exp = Column(Integer)
    worker_exp = Column(Integer)
    worker1 = Column(String)
    worker2 = Column(String)
    worker3 = Column(String)
    favor = Column(Integer)
    airship_power = Column(Integer)
    collection_score = Column(Integer)
    energy_score = Column(Integer)
    energy_cost = Column(Integer)
    base_crafting_time = Column(String)

    def __repr__(self) -> str:
        return f'Item {Item.name}; Tier:{Item.tier};'


class MarketStats(Base):
    __tablename__ = "marketstats"
    id = Column(Integer, primary_key=True)
    item_id = relationship('Item', foreign_keys='Item.id', cascade="all, delete-orphan")
    gold_price = Column(Integer)
    gold_qty = Column(Integer)
    gems_price = Column(Integer)
    gems_qty = Column(Integer)
    received_at = Column(DateTime)


Base.metadata.create_all(engine)
