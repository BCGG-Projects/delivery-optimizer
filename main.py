from data_generator import DataGenerator
from route_planner import RoutePlanner
from visualisation import plot_solution


def main():
    generator = DataGenerator()
    data = generator.generate()

    warehouses = data['warehouses']
    clients = data['clients']
    vehicles = data['vehicles']

    planner = RoutePlanner(warehouses, clients, vehicles)
    best_solution = planner.plan_routes()

    plot_solution(warehouses, vehicles, best_solution)


if __name__ == "__main__":
    main()
