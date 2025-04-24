import random
import json
from typing import List, Dict


def to_json(data: Dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


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

    def generate_coordinates(self) -> Dict[str, int]:
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

            vehicle = {
                "id": vehicle_id,
                "type": vehicle_type,
                "capacity": capacity,
                "warehouse_id": assigned_warehouse,
            }
            self.vehicles.append(vehicle)

    def generate_clients(self):
        for i in range(self.num_clients):
            client_id = f"C{i}"
            coordinates = self.generate_coordinates()
            delivery_type = random.choice(["delivery", "pickup"])
            total_weight = random.randint(100, 200)
            goods = {good: 0 for good in self.goods_types}
            remaining_weight = total_weight

            while remaining_weight > 0:
                selected_good = random.choice(self.goods_types)
                weight = random.randint(1, remaining_weight)
                goods[selected_good] += weight
                remaining_weight -= weight

            client = {
                "id": client_id,
                **coordinates,
                "type": delivery_type,
                "goods": goods,
            }
            self.clients.append(client)

    def generate(self) -> Dict[str, List[Dict]]:
        self.generate_warehouses()
        self.generate_clients()
        self.generate_vehicles()

        return {
            "warehouses": self.warehouses,
            "clients": self.clients,
            "vehicles": self.vehicles,
            "cat_vehicle": self.cat_vehicle_id,
        }
