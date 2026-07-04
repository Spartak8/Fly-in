from pathfinding import Pathfinding
from models import Zone, StartHub, EndHub, Graph, Drone


class Simulation:
    def __init__(self, graph: Graph, nb_drones: int):
        self.graph = graph
        self.nb_drones = nb_drones
        self.start = self._find_zone_class(StartHub)
        self.end = self._find_zone_class(EndHub)
        self.start_name = self.start.name
        self.end_name = self.end.name
        self.drones = self._create_drones()
        self.pathfind = Pathfinding(self.graph)
        self.result = self.pathfind.shortest_path(self.start_name, self.end_name)
        if self.result is None:
            raise ValueError(f"No path exists from {self.start_name} to {self.end_name}")
        self.path, self.total_cost = self.result
        for drone in self.drones:
            drone.path = self.path
        self.occupancy = {name: [] for name in self.graph.zones}
        self.occupancy[self.start_name] = list(self.drones)

    def _find_zone_class(self, zone_class: Zone):
        for zone in self.graph.zones.values():
            if isinstance(zone, zone_class):
                return zone
        return None

    def _create_drones(self):
        drones = []
        drone_id = 1
        for i in range(self.nb_drones):
            drone = Drone(drone_id, self.start)
            drones.append(drone)
            drone_id += 1
        return drones
