from typing import List, Dict, Optional, Type
from pathfinding import Pathfinding
from models import Zone, StartHub, EndHub, Graph, Drone, Connection


class Simulation:
    """Manages the overall simulation of drones navigating the graph."""

    def __init__(self, graph: Graph, nb_drones: int) -> None:
        """Initializes the Simulation instance.

        Args:
            graph (Graph): The network graph.
            nb_drones (int): Total number of drones.

        Raises:
            ValueError: If no path exists from start to end.
        """
        self.graph: Graph = graph
        self.nb_drones: int = nb_drones

        start_zone = self._find_zone_class(StartHub)
        end_zone = self._find_zone_class(EndHub)
        if start_zone is None or end_zone is None:
            raise ValueError("StartHub or EndHub missing")

        self.start: Zone = start_zone
        self.end: Zone = end_zone
        self.start_name: str = self.start.name
        self.end_name: str = self.end.name
        self.drones: List[Drone] = self._create_drones()
        self.pathfind: Pathfinding = Pathfinding(self.graph)
        self.distances: Dict[str, float] = self.pathfind.distances_to_goal(
            self.end_name)

        if self.distances[self.start_name] == float('inf'):
            raise ValueError(f"No path exists to {self.end_name}")

        self.occupancy: Dict[str, List[Drone]] = {
            name: [] for name in self.graph.zones
        }
        self.occupancy[self.start_name] = list(self.drones)
        self.connection_occupancy: Dict[Connection, List[Drone]] = {
            conn: [] for conn in self.graph.connections
        }

    def _find_zone_class(self, zone_class: Type[Zone]) -> Optional[Zone]:
        """Finds the first zone matching a specific class.

        Args:
            zone_class (type): The class type to find.

        Returns:
            Zone or None: Matching zone object.
        """
        for zone in self.graph.zones.values():
            if isinstance(zone, zone_class):
                return zone
        return None

    def _create_drones(self) -> List[Drone]:
        """Creates and initializes all drones at the starting hub.

        Returns:
            list: List of initialized Drone objects.
        """
        drones: List[Drone] = []
        drone_id = 1
        for _ in range(self.nb_drones):
            drone = Drone(drone_id, self.start)
            drones.append(drone)
            drone_id += 1
        return drones

    def _find_connection(self, zone1_name: str,
                         zone2_name: str) -> Optional[Connection]:
        """Finds the connection object between two zones.

        Args:
            zone1_name (str): The name of the first zone.
            zone2_name (str): The name of the second zone.

        Returns:
            Connection or None: The connecting object.
        """
        for connection in self.graph.connections:
            if (connection.zone1 == zone1_name and
                    connection.zone2 == zone2_name):
                return connection
            if (connection.zone1 == zone2_name and
                    connection.zone2 == zone1_name):
                return connection
        return None

    def _advance_drone(self, drone: Drone) -> Optional[str]:
        """Attempts to advance a drone along its path.

        Args:
            drone (Drone): The drone to advance.

        Returns:
            str or None: Movement string.
        """
        if drone.fly_left > 0:
            drone.fly_left -= 1
            if drone.fly_left == 0:
                if drone.flying_to is None or drone.using_connection is None:
                    return None
                new_zone_name = drone.flying_to
                new_zone = self.graph.zones[new_zone_name]
                drone.current_zone = new_zone
                drone.flying_to = None
                self.connection_occupancy[drone.using_connection].remove(drone)
                drone.using_connection = None
                if new_zone == self.end:
                    drone.arrived = True
                return f"D{drone.drone_id}-{new_zone_name}"
            else:
                conn_name = f"{drone.current_zone.name}-{drone.flying_to}"
                return f"D{drone.drone_id}-{conn_name}"

        next_zone_name = self._choose_next_zone(drone)
        if next_zone_name is None:
            return None

        next_zone = self.graph.zones[next_zone_name]
        current_count = len(self.occupancy[next_zone_name])
        if not next_zone.has_capacity(current_count):
            return None

        connection = self._find_connection(drone.current_zone.name,
                                           next_zone_name)
        if connection is None:
            return None

        current_link_count = len(self.connection_occupancy[connection])
        if current_link_count >= connection.max_link_capacity:
            return None

        cost = next_zone.movement_cost()
        if cost is None:
            return None

        drone.fly_left = cost
        drone.flying_to = next_zone_name
        self.occupancy[drone.current_zone.name].remove(drone)
        self.occupancy[next_zone_name].append(drone)
        self.connection_occupancy[connection].append(drone)
        drone.using_connection = connection
        drone.fly_left -= 1

        if drone.fly_left == 0:
            drone.current_zone = next_zone
            drone.flying_to = None
            self.connection_occupancy[connection].remove(drone)
            drone.using_connection = None
            if next_zone == self.end:
                drone.arrived = True
            return f"D{drone.drone_id}-{next_zone_name}"
        else:
            conn_name = f"{drone.current_zone.name}-{next_zone_name}"
            return f"D{drone.drone_id}-{conn_name}"

    def _choose_next_zone(self, drone: Drone) -> Optional[str]:
        """Chooses the best next zone for a drone to move into.

        Args:
            drone (Drone): The drone that needs a new destination.

        Returns:
            str or None: Chosen next zone name.
        """
        current_name = drone.current_zone.name
        current_distance = self.distances[current_name]
        neighbours = self.pathfind.get_neighbour(current_name)
        candidates: List[str] = []
        for neighbour in neighbours:
            neighbour_distance = self.distances[neighbour]
            if neighbour_distance < current_distance:
                next_zone = self.graph.zones[neighbour]
                current_count = len(self.occupancy[neighbour])
                if not next_zone.has_capacity(current_count):
                    continue
                connection = self._find_connection(current_name, neighbour)
                if connection is None:
                    continue
                current_link_count = len(self.connection_occupancy[connection])
                if current_link_count >= connection.max_link_capacity:
                    continue
                candidates.append(neighbour)
        if not candidates:
            return None

        def key_func(x: str) -> tuple[bool, int]:
            zone = self.graph.zones[x]
            is_priority = zone.zone_type == "priority"
            spare_capacity = zone.max_drones - len(self.occupancy[x])
            return (is_priority, spare_capacity)
        return max(candidates, key=key_func)

    def run(self) -> List[List[str]]:
        """Executes the simulation turns.

        Returns:
            list: Turns with movement strings.

        Raises:
            RuntimeError: If turns exceed maximum limit.
        """
        turns: List[List[str]] = []
        max_turns = 10000
        turn_count = 0
        while not all(drone.arrived for drone in self.drones):
            if turn_count >= max_turns:
                raise RuntimeError("Exceeded maximum turn limit")
            turn_moves: List[str] = []
            for drone in self.drones:
                if drone.arrived:
                    continue
                result = self._advance_drone(drone)
                if result is not None:
                    turn_moves.append(result)
            turns.append(turn_moves)
            turn_count += 1
        return turns
