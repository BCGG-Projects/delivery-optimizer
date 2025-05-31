import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

def plot_solution(warehouses, vehicles, best_solution):
    plt.figure(figsize=(10, 10))
    plt.xlim(0, 100)
    plt.ylim(0, 100)

    for warehouse in warehouses:
        plt.scatter(warehouse['x'], warehouse['y'], marker='*', color='black', s=200, label='Warehouse')

    colors = cm.rainbow(np.linspace(0, 1, len(vehicles)))

    for color, vehicle in zip(colors, vehicles):
        vehicle_id = vehicle['id']
        route = best_solution[vehicle_id]

        if not route:
            continue

        warehouse = next(w for w in warehouses if w['id'] == vehicle['warehouse_id'])
        path_x = [warehouse['x']]
        path_y = [warehouse['y']]

        for client in route:
            path_x.append(client['x'])
            path_y.append(client['y'])

        path_x.append(warehouse['x'])
        path_y.append(warehouse['y'])

        plt.plot(path_x, path_y, marker='o', color=color, label=f"{vehicle_id} ({vehicle['type']})")
        plt.scatter(path_x[1:-1], path_y[1:-1], color=color, s=30)

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.title("Vehicle Routes")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
