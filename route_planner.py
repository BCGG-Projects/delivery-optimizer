import logging
import math
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


class RoutePlanner:
    """
    Assigns clients to vehicles via centroidal Voronoi, then builds
    multi-type, capacity-aware routes using nearby pickups/deliveries.
    """

    def __init__(self, warehouses, clients, vehicles, max_iters=10, tol=1e-2):
        """
        warehouses: list of {'id': int, 'x': float, 'y': float}
        clients:    list of {'id': int, 'x': float, 'y': float,
                              'demand': {good: float,...}, 'is_pickup': bool}
        vehicles:   list of {'id': int, 'type': str, 'capacity': float, 'warehouse_id': int}
        """
        self.warehouses = {wh["id"]: np.array((wh["x"], wh["y"]), dtype=float)
                           for wh in warehouses}
        self.clients = {c["id"]: np.array((c["x"], c["y"]), dtype=float)
                        for c in clients}
        self.demands = {c["id"]: c["demand"] for c in clients}
        self.is_pickup = {c["id"]: c["is_pickup"] for c in clients}
        self.vehicles = vehicles
        self.vehicle_ids = [v["id"] for v in vehicles]
        self.wh_map = {v["id"]: v["warehouse_id"] for v in vehicles}
        self.capacities = {v["id"]: v["capacity"] for v in vehicles}
        self.centers = {vid: self.warehouses[self.wh_map[vid]].copy()
                        for vid in self.vehicle_ids}
        self.max_iters = max_iters
        self.tol = tol
        self.good_types = list(next(iter(self.demands.values())).keys())
        logger.info(f"Initialized RoutePlanner: {len(self.vehicles)} vehicles, {len(self.clients)} clients")

    def assign_clients(self):
        """
        Assign each client to nearest vehicle center.
        Returns {vehicle_id: [client_id, ...], ...}
        """
        assignment = {vid: [] for vid in self.vehicle_ids}
        for cid, coord in self.clients.items():
            nearest_vid = min(
                self.centers.keys(),
                key=lambda vid: np.linalg.norm(coord - self.centers[vid])
            )
            assignment[nearest_vid].append(cid)
        return assignment

    def update_centers(self, assignment):
        """
        Recompute each vehicle center as centroid of assigned clients + its warehouse.
        Returns total shift.
        """
        total_shift = 0.0
        new_centers = {}
        for vid, cids in assignment.items():
            pts = [self.clients[cid] for cid in cids]
            pts.append(self.warehouses[self.wh_map[vid]])
            centroid = np.mean(pts, axis=0)
            total_shift += np.linalg.norm(centroid - self.centers[vid])
            new_centers[vid] = centroid
        self.centers = new_centers
        return total_shift

    def plan_routes(self):
        """
        Run centroidal Voronoi assignment, then build multi-type routes.
        Returns {vehicle_id: [(x1,y1), (x2,y2), ...], ...}
        """
        assignment = {}
        for it in range(self.max_iters):
            assignment = self.assign_clients()
            shift = self.update_centers(assignment)
            logger.info(f"Iteration {it}: shift = {shift:.4f}")
            if shift < self.tol:
                break

        solution = {}
        for vid, cids in assignment.items():
            depot = tuple(self.warehouses[self.wh_map[vid]])
            logger.info(f"Vehicle {vid}: building route for {len(cids)} clients")
            route = self._build_capacity_route(vid, depot, cids)
            solution[vid] = route
        return solution

    def _build_capacity_route(self, vid, depot, cids):
        """
        vid:       ID of vehicle
        depot:     (x, y) warehouse coordinates
        cids:      list of client IDs assigned to this vehicle
        """
        unserved = set(cids)
        locs = {cid: tuple(self.clients[cid]) for cid in cids}
        demands = {cid: self.demands[cid] for cid in cids}
        is_pickup = {cid: self.is_pickup[cid] for cid in cids}
        good_types = self.good_types
        capacity = self.capacities[vid]

        total_demands = {g: 0.0 for g in good_types}
        for cid in cids:
            if not is_pickup[cid]:
                for g, amt in demands[cid].items():
                    total_demands[g] += amt

        inventory = {g: 0.0 for g in good_types}
        cap_left = capacity
        for g in good_types:
            if total_demands[g] <= 0:
                continue
            to_load = min(total_demands[g], cap_left)
            inventory[g] = to_load
            cap_left -= to_load
            if cap_left <= 0:
                break

        logger.info(f"Vehicle {vid}: initial load from depot = {inventory} (cap_left={cap_left:.1f})")

        route = [depot]
        current_loc = depot

        def euclid(a, b):
            return math.hypot(a[0] - b[0], a[1] - b[1])

        def total_inventory(inv):
            return sum(inv.values())

        while unserved:
            feasible = []
            for cid in unserved:
                dvec = demands[cid]
                if is_pickup[cid]:
                    pickup_weight = sum(-amt for amt in dvec.values())
                    if total_inventory(inventory) + pickup_weight <= capacity:
                        feasible.append(cid)
                else:
                    ok = True
                    for g, amt in dvec.items():
                        if inventory[g] < amt:
                            ok = False
                            break
                    if ok:
                        feasible.append(cid)

            if feasible:
                next_cid = min(feasible, key=lambda cid: euclid(current_loc, locs[cid]))
                dvec = demands[next_cid]
                loc = locs[next_cid]
                route.append(loc)
                current_loc = loc

                if is_pickup[next_cid]:
                    picked = {}
                    for g, amt in dvec.items():
                        pickup_amt = -amt
                        inventory[g] += pickup_amt
                        picked[g] = pickup_amt
                    logger.info(f"Vehicle {vid}: picked up {picked} at client {next_cid}, inventory now={inventory}")
                else:
                    delivered = {}
                    for g, amt in dvec.items():
                        inventory[g] -= amt
                        delivered[g] = amt
                    logger.info(f"Vehicle {vid}: delivered {delivered} to client {next_cid}, inventory now={inventory}")

                unserved.remove(next_cid)

            else:
                nearest_client = min(unserved, key=lambda cid: euclid(current_loc, locs[cid]))
                dist_client = euclid(current_loc, locs[nearest_client])
                nearest_wh = min(
                    self.warehouses.keys(),
                    key=lambda wid: euclid(current_loc, tuple(self.warehouses[wid]))
                )
                wh_loc = tuple(self.warehouses[nearest_wh])
                dist_wh = euclid(current_loc, wh_loc)

                if dist_client < dist_wh:
                    cid = nearest_client
                    dvec = demands[cid]
                    if is_pickup[cid]:
                        weight = sum(-amt for amt in dvec.values())
                        if total_inventory(inventory) + weight <= capacity:
                            route.append(locs[cid])
                            current_loc = locs[cid]
                            picked = {}
                            for g, amt in dvec.items():
                                pickup_amt = -amt
                                inventory[g] += pickup_amt
                                picked[g] = pickup_amt
                            logger.info(f"Vehicle {vid}: picked up {picked} at client {cid}, inventory now={inventory}")
                            unserved.remove(cid)
                            continue
                    else:
                        ok = True
                        for g, amt in dvec.items():
                            if inventory[g] < amt:
                                ok = False
                                break
                        if ok:
                            route.append(locs[cid])
                            current_loc = locs[cid]
                            delivered = {}
                            for g, amt in dvec.items():
                                inventory[g] -= amt
                                delivered[g] = amt
                            logger.info(f"Vehicle {vid}: delivered {delivered} to client {cid}, inventory now={inventory}")
                            unserved.remove(cid)
                            continue

                route.append(wh_loc)
                current_loc = wh_loc
                for g in inventory:
                    inventory[g] = 0.0

                deliveries = [
                    (cid, demands[cid]) for cid in unserved
                    if not is_pickup[cid]
                ]
                deliveries.sort(key=lambda item: sum(item[1].values()))

                cap_left = capacity
                new_inv = {g: 0.0 for g in good_types}
                loaded_clients = []
                for cid, dvec in deliveries:
                    weight = sum(dvec.values())
                    if weight <= cap_left:
                        for g, amt in dvec.items():
                            new_inv[g] += amt
                        cap_left -= weight
                        loaded_clients.append(cid)

                inventory = new_inv
                logger.info(f"Vehicle {vid}: reloaded for deliveries {loaded_clients} at warehouse {nearest_wh}, inventory now={inventory}")

        if current_loc != depot:
            route.append(depot)

        return route
