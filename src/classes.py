class Item:
    def __init__(self, name, market, tier, item_type, image, gold_qty, gems_qty, gold_price, gems_price, base_value, item_class):
        self.name = name
        self.market = market
        self.tier = tier
        self.item_type = item_type
        self.image = image
        self.gold_qty = gold_qty
        self.gems_qty = gems_qty
        self.gold_price = gold_price
        self.gems_price = gems_price
        self.base_value = base_value
        self.item_class = item_class

    def __str__(self):
        return f'Name:{self.name}; Market:{self.market}; Tier:{self.tier}; Item type:{self.item_type};' \
               f' Gold:{self.gold_price}; Gems:{self.gems_price}; Item class:{self.item_class};'
