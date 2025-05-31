import random


class DataGenerator:
    def __init__(
        self,
        num_warehouses: int = 5,
        num_clients: int = 20,
        min_vehicles: int = 3,
        max_vehicles: int = 6,
        coordinate_range: int = 100,
    ):
        self.num_warehouses = num_warehouses
        self.num_clients = num_clients
        self.num_vehicles = random.randint(min_vehicles, max_vehicles)
        self.coordinate_range = coordinate_range

        self.vehicle_types = {"green": 1000, "blue": 1500, "red": 2000}
        self.goods_types = ["oranges", "uranium", "tuna"]

        self.warehouses = []
        self.clients = []
        self.vehicles = []
        self.cat_vehicle_id = None

    def distribute_weight(self, total_weight, parts):
        cuts = sorted([0] + [random.randint(0, total_weight) for _ in range(parts - 1)] + [total_weight])
        return [cuts[i+1] - cuts[i] for i in range(parts)]

    def generate_coordinates(self) -> dict[str, int]:
        return {
            "x": random.randint(0, self.coordinate_range),
            "y": random.randint(0, self.coordinate_range),
        }

    def generate_warehouses(self):
        self.warehouses = [
            {"id": f"W{i}", **self.generate_coordinates()}
            for i in range(self.num_warehouses)
        ]

    def generate_vehicles(self):
        for i in range(self.num_vehicles):
            vehicle_id = f"V{i}"
            vehicle_type = random.choice(list(self.vehicle_types.keys()))
            capacity = self.vehicle_types[vehicle_type]
            assigned_warehouse = random.choice(self.warehouses)["id"]

            self.vehicles.append(
                {
                    "id": vehicle_id,
                    "type": vehicle_type,
                    "capacity": capacity,
                    "warehouse_id": assigned_warehouse,
                }
            )

    def generate_clients(self):
        for i in range(self.num_clients):
            client_id = f"C{i}"
            coordinates = self.generate_coordinates()
            delivery_type = random.choice(["delivery", "pickup"])
        
            total_weight = random.randint(100, 200) if delivery_type == "delivery" else random.randint(-200, -100)

            num_goods = random.randint(1, len(self.goods_types))
            selected_goods_types = random.sample(self.goods_types, num_goods)

            goods_distribution = self.distribute_weight(abs(total_weight), len(selected_goods_types))

            goods = {}
            for good_type, good_weight in zip(selected_goods_types, goods_distribution):
                goods[good_type] = good_weight if total_weight > 0 else -good_weight

            self.clients.append(
                {
                "id": client_id,
                **coordinates,
                "type": delivery_type,
                "goods": goods,
                }
            )

    def generate(self) -> dict[str, list[dict]]:
        self.generate_warehouses()
        self.generate_clients()
        self.generate_vehicles()

        return {
            "warehouses": self.warehouses,
            "clients": self.clients,
            "vehicles": self.vehicles,
            "cat_vehicle": self.cat_vehicle_id,
        }
