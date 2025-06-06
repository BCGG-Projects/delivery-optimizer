from data_generator import DataGenerator
from route_planner import RoutePlanner
from visualisation import plot_solution
import math

def main():
    generator = DataGenerator()
    data = generator.generate()
    warehouses = data["warehouses"]
    clients = data["clients"]
    vehicles = data["vehicles"]

    planner = RoutePlanner(warehouses, clients, vehicles)
    solution = planner.plan_routes()

    for vid, route in solution.items():
        total_length = 0.0
        for i in range(len(route) - 1):
            x1, y1 = route[i]
            x2, y2 = route[i + 1]
            total_length += math.hypot(x2 - x1, y2 - y1)
        print(f"Vehicle {vid} total route length: {total_length:.2f}")

    plot_solution(warehouses, vehicles, solution)

if __name__ == "__main__":
    main()
