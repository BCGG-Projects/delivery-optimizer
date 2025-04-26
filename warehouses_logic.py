import random
from data_generator import DataGenerator

class WarehousesLogic:
    def __init__(self, warehouses):
        self.warehouses = warehouses
        self.goods_types = ["oranges", "uranium", "tuna"]
        self.list = []

    def show_warehouses(self):
        for warehouse in self.warehouses:
            delivery_or_pickup = random.choice([0, 1])

            weight = random.randint(100, 200) if delivery_or_pickup == 1 else random.randint(-200, -100)
            warehouse["weight"] = weight

            num_goods = random.randint(1, len(self.goods_types))

            selected_goods_types = random.sample(self.goods_types, num_goods)
            goods_distribution = self.distribute_weight(abs(weight), len(selected_goods_types))

            goods = {}
            for good_type, good_weight in zip(selected_goods_types, goods_distribution):
                goods[good_type] = -good_weight if weight < 0 else good_weight

            warehouse["goods"] = goods

        return self.warehouses

    def distribute_weight(self, total_weight, parts):
        cuts = sorted([0] + [random.randint(0, total_weight) for _ in range(parts - 1)] + [total_weight])
        return [cuts[i+1] - cuts[i] for i in range(parts)]