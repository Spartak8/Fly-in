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

    def _can_move(self, drone):
        if drone.path_index + 1 >= len(drone.path):
            return False
        next_zone_name = drone.path[drone.path_index + 1]
        next_zone = self.graph.zones[next_zone_name]
        current_count = len(self.occupancy[next_zone_name])
        return next_zone.has_capacity(current_count)

    def _move_drone(self, drone):
        new_zone_name = drone.path[drone.path_index + 1]
        self.occupancy[drone.current_zone.name].remove(drone)
        self.occupancy[new_zone_name].append(drone)
        drone.current_zone = self.graph.zones[new_zone_name]
        drone.path_index += 1
        if drone.current_zone == self.end:
            drone.arrived = True

    def _advance_drone(self,drone):
        

    def run(self):
        turns = []
        max_turns = 10000
        turn_count = 0
        while not all(drone.arrived for drone in self.drones):
            if turn_count >= max_turns:
                raise RuntimeError("Simulation exceeded maximum turn limit — possible deadlock")
            turn_moves = []
            for drone in self.drones:
                if drone.arrived:
                    continue
                if self._can_move(drone):
                    self._move_drone(drone)
                    turn_moves.append(f"D{drone.drone_id}-{drone.current_zone.name}")
            turns.append(turn_moves)
            turn_count += 1
        return turns
    

if __name__ == "__main__":
    from parser import Parser

    parser = Parser("maps/challenger/01_the_impossible_dream.txt")
    nb_drones, graph = parser.parse()

    sim = Simulation(graph, nb_drones)
    turns = sim.run()

    for turn_moves in turns:
        print(" ".join(turn_moves))

    print(f"\nTotal turns: {len(turns)}")
