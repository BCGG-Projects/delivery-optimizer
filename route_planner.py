import logging
import math
import numpy as np
from ortools.constraint_solver import routing_enums_pb2, pywrapcp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class RoutePlanner:
    """
    Approach: Assign clients directly to vehicles using a centroidal Voronoi (k-means-like) scheme,
    then solve TSP per vehicle.

    Steps:
      1. Initialize vehicle centers at their warehouse coordinates.
      2. Repeat until convergence or max_iters:
         a. Assign each client to the nearest vehicle center.
         b. Recompute each vehicle center as the centroid of its assigned clients + warehouse.
      3. For each vehicle, solve closed TSP (start/end at warehouse).
    """
    def __init__(self, warehouses, clients, vehicles, max_iters=10, tol=1e-2):
        self.warehouses = {wh['id']: np.array((wh['x'], wh['y'])) for wh in warehouses}
        self.clients    = {c['id']: np.array((c['x'], c['y'])) for c in clients}
        self.vehicles   = vehicles
        self.vehicle_ids = [v['id'] for v in vehicles]
        self.wh_map      = {v['id']: v['warehouse_id'] for v in vehicles}
        self.centers     = {vid: self.warehouses[self.wh_map[vid]].copy() for vid in self.vehicle_ids}
        self.max_iters   = max_iters
        self.tol         = tol
        logger.info(f"RoutePlanner initialized with {len(self.vehicles)} vehicles and {len(self.clients)} clients.")

    def assign_clients(self):
        """Assigns each client to the nearest vehicle center."""
        assignment = {vid: [] for vid in self.vehicle_ids}
        for cid, coord in self.clients.items():
            dists = {vid: np.linalg.norm(coord - ctr) for vid, ctr in self.centers.items()}
            nearest_vid = min(dists, key=dists.get)
            assignment[nearest_vid].append(cid)
        return assignment

    def update_centers(self, assignment):
        """Updates centers as the centroid of their assigned clients plus the warehouse location."""
        total_shift = 0.0
        new_centers = {}
        for vid, cids in assignment.items():
            points = [self.clients[cid] for cid in cids]
            points.append(self.warehouses[self.wh_map[vid]])
            centroid = np.mean(points, axis=0)
            total_shift += np.linalg.norm(centroid - self.centers[vid])
            new_centers[vid] = centroid
        self.centers = new_centers
        return total_shift

    def plan_routes(self):
        for iteration in range(self.max_iters):
            assignment = self.assign_clients()
            shift = self.update_centers(assignment)
            logger.info(f"Iteration {iteration}: center shift = {shift:.4f}")
            if shift < self.tol:
                break

        solution = {}
        for vid, cids in assignment.items():
            depot = tuple(self.warehouses[self.wh_map[vid]])
            coords = [tuple(self.clients[cid]) for cid in cids]
            logger.info(f"Vehicle {vid}: {len(cids)} clients assigned; computing TSP...")
            route = self._solve_tsp(depot, coords)
            solution[vid] = route
        return solution

    def _solve_tsp(self, depot, clients_coords):
        """Solves a closed TSP (return to depot) for one vehicle."""
        points = [depot] + clients_coords
        n = len(points)
        dist_matrix = [
            [int(math.hypot(points[i][0] - points[j][0], points[i][1] - points[j][1]))
             for j in range(n)]
            for i in range(n)
        ]
        manager = pywrapcp.RoutingIndexManager(n, 1, 0)
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(i, j):
            return dist_matrix[manager.IndexToNode(i)][manager.IndexToNode(j)]

        transit = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit)

        search_params = pywrapcp.DefaultRoutingSearchParameters()
        search_params.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_params.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_params.time_limit.seconds = 5

        routing.AddDimension(transit, 0, 10**9, True, 'Distance')

        solution = routing.SolveWithParameters(search_params)
        if not solution:
            logger.error("TSP solver failed to find a solution.")
            return []

        index = routing.Start(0)
        route = []
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            if node != 0:
                route.append(points[node])
            index = solution.Value(routing.NextVar(index))
        return route
