import random

class DataGenerator:
    """
    Generates warehouses, clients, and vehicles.
    """

    def __init__(self,
                 n_warehouses=5,
                 n_clients=500,
                 n_vehicles=6,
                 coord_range=(0, 100),
                 total_demand_range=(100, 200)):
        self.n_warehouses = n_warehouses
        self.n_clients = n_clients
        self.n_vehicles = n_vehicles
        self.coord_min, self.coord_max = coord_range
        self.demand_min, self.demand_max = total_demand_range
        self.good_types = ["oranges", "uranium", "tuna"]
        self.vehicle_types = [
            {"type": "green", "capacity": 1000.0},
            {"type": "blue",  "capacity": 1500.0},
            {"type": "red",   "capacity": 2000.0},
        ]

    def generate_warehouses(self):
        """
        Returns a list of warehouses:
        [{'id': int, 'x': float, 'y': float}, ...]
        """
        warehouses = []
        for wid in range(self.n_warehouses):
            x = random.uniform(self.coord_min, self.coord_max)
            y = random.uniform(self.coord_min, self.coord_max)
            warehouses.append({"id": wid, "x": x, "y": y})
        return warehouses

    def generate_clients(self):
        """
        Returns a list of clients:
        [{'id': int, 'x': float, 'y': float, 'demand': {good: float, ...}, 'is_pickup': bool}, ...]
        """
        clients = []
        for cid in range(self.n_clients):
            x = random.uniform(self.coord_min, self.coord_max)
            y = random.uniform(self.coord_min, self.coord_max)
            total = random.uniform(self.demand_min, self.demand_max)
            cuts = sorted([random.uniform(0, total) for _ in range(len(self.good_types) - 1)])
            parts = []
            prev = 0.0
            for cut in cuts:
                parts.append(cut - prev)
                prev = cut
            parts.append(total - prev)
            demand_vector = {self.good_types[i]: parts[i] for i in range(len(self.good_types))}
            is_pickup = random.choice([True, False])
            if is_pickup:
                demand_vector = {g: -amt for g, amt in demand_vector.items()}
            clients.append({
                "id": cid,
                "x": x,
                "y": y,
                "demand": demand_vector,
                "is_pickup": is_pickup
            })
        return clients

    def generate_vehicles(self):
        """
        Returns a list of vehicles:
        [{'id': int, 'type': str, 'capacity': float, 'warehouse_id': int}, ...]
        """
        vehicles = []
        for vid in range(self.n_vehicles):
            vt = random.choice(self.vehicle_types)
            vehicles.append({
                "id": vid,
                "type": vt["type"],
                "capacity": vt["capacity"],
                "warehouse_id": random.randrange(self.n_warehouses)
            })
        return vehicles

    def generate(self):
        """
        Returns dict with keys 'warehouses', 'clients', 'vehicles'
        """
        return {
            "warehouses": self.generate_warehouses(),
            "clients": self.generate_clients(),
            "vehicles": self.generate_vehicles()
        }
