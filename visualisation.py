import matplotlib.pyplot as plt

def plot_solution(warehouses, vehicles, solution):
    """
    warehouses: list of {'id': int, 'x': float, 'y': float}
    vehicles:   list of {'id': int, 'warehouse_id': int, 'capacity': float, 'type': str}
    solution:   dict {vehicle_id: [(x,y), ...], ...}
    """
    for vid, route in solution.items():
        path_x, path_y = [], []
        vehicle = next(v for v in vehicles if v["id"] == vid)
        wh = next(w for w in warehouses if w["id"] == vehicle["warehouse_id"])

        path_x.append(wh["x"])
        path_y.append(wh["y"])
        for (x, y) in route:
            path_x.append(x)
            path_y.append(y)
        path_x.append(wh["x"])
        path_y.append(wh["y"])

        label = f"Vehicle {vid} ({vehicle['type']}, cap: {vehicle['capacity']:.0f})"
        plt.plot(path_x, path_y, marker="o", label=label)

    wh_x = [w["x"] for w in warehouses]
    wh_y = [w["y"] for w in warehouses]
    plt.scatter(wh_x, wh_y, marker="*", s=150, c="k", label="Warehouses")

    plt.xlabel("X coordinate")
    plt.ylabel("Y coordinate")
    plt.title("Vehicle Routes (by type)")
    plt.legend()
    plt.grid(True)
    plt.show()
