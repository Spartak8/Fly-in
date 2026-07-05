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
        self.connection_occupancy = {conn: [] for conn in self.graph.connections}

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

    def _find_connection(self, zone1_name, zone2_name):
        for connection in self.graph.connections:
            if connection.zone1 == zone1_name and connection.zone2 == zone2_name:
                return connection
            if connection.zone1 == zone2_name and connection.zone2 == zone1_name:
                return connection
        return None

    def _advance_drone(self, drone):
        if drone.fly_left > 0:
            drone.fly_left -= 1
            if drone.fly_left == 0:
                new_zone_name = drone.flying_to
                new_zone = self.graph.zones[new_zone_name]
                drone.current_zone = new_zone
                drone.path_index += 1
                drone.flying_to = None
                self.connection_occupancy[drone.using_connection].remove(drone)
                drone.using_connection = None
                if new_zone == self.end:
                    drone.arrived = True
                return f"D{drone.drone_id}-{new_zone_name}"
            else:
                connection_name = f"{drone.current_zone.name}-{drone.flying_to}"
                return f"D{drone.drone_id}-{connection_name}"

        if drone.path_index + 1 >= len(drone.path):
            return
        next_zone_name = drone.path[drone.path_index + 1]
        next_zone = self.graph.zones[next_zone_name]
        current_count = len(self.occupancy[next_zone_name])
        if not next_zone.has_capacity(current_count):
            return
        connection = self._find_connection(drone.current_zone.name, next_zone_name)
        current_link_count = len(self.connection_occupancy[connection])
        if current_link_count >= connection.max_link_capacity:
            return
        next_zone_name = drone.path[drone.path_index + 1]
        next_zone = self.graph.zones[next_zone_name]
        drone.fly_left = next_zone.movement_cost()
        drone.flying_to = next_zone_name
        self.occupancy[drone.current_zone.name].remove(drone)
        self.occupancy[next_zone_name].append(drone)
        self.connection_occupancy[connection].append(drone)
        drone.using_connection = connection
        drone.fly_left -= 1
        if drone.fly_left == 0:
            drone.current_zone = next_zone
            drone.path_index += 1
            drone.flying_to = None
            self.connection_occupancy[connection].remove(drone)
            drone.using_connection = None
            if next_zone == self.end:
                drone.arrived = True
            return f"D{drone.drone_id}-{next_zone_name}"
        else:
            connection_name = f"{drone.current_zone.name}-{next_zone_name}"
            return f"D{drone.drone_id}-{connection_name}"

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
                result = self._advance_drone(drone)
                if result is not None:
                    turn_moves.append(result)
            turns.append(turn_moves)
            turn_count += 1
        return turns


if __name__ == "__main__":
    from parser import Parser

    parser = Parser("maps/hard/01_maze_nightmare.txt")
    nb_drones, graph = parser.parse()

    sim = Simulation(graph, nb_drones)
    turns = sim.run()

    for turn_moves in turns:
        print(" ".join(turn_moves))

    print(f"\nTotal turns: {len(turns)}")
