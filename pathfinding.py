from typing import Tuple, Dict, List, Optional, Set
from models import Graph


class Pathfinding:
    """Handles pathfinding logic over a network graph using Dijkstra's."""

    def __init__(self, graph: Graph) -> None:
        """Initializes the Pathfinding instance.

        Args:
            graph (Graph): The graph of zones and connections.
        """
        self.graph: Graph = graph

    def shortest_path(self, start: str,
                      end: str) -> Optional[Tuple[List[str], int]]:
        """Finds the shortest path between two zones.

        Args:
            start (str): The name of the starting zone.
            end (str): The name of the destination zone.

        Returns:
            tuple or None: Path (list of str) and total cost (int).
        """
        distances: Dict[str, float] = {
            zone: float('inf') for zone in self.graph.zones
        }
        distances[start] = 0
        previous: Dict[str, str] = {}
        visited: Set[str] = set()

        while True:
            current: Optional[str] = self._get_closest_unvisited_zone(
                distances, visited)
            if current is None:
                break
            if current == end:
                break
            visited.add(current)

            for neighbour in self.get_neighbour(current):
                if neighbour in visited:
                    continue
                neigh_zone = self.graph.zones[neighbour]
                cost = neigh_zone.movement_cost()
                if cost is None:
                    continue
                new_distance = distances[current] + cost
                if new_distance < distances[neighbour]:
                    distances[neighbour] = new_distance
                    previous[neighbour] = current

        if end not in previous and end != start:
            return None

        total_cost: int = int(distances[end])
        path: List[str] = []
        now: str = end
        while now != start:
            path.append(now)
            now = previous[now]
        path.append(start)
        path.reverse()
        return path, total_cost

    def distances_to_goal(self, end_name: str) -> Dict[str, float]:
        """Calculates the shortest distance from all zones to a goal zone.

        Args:
            end_name (str): The name of the goal zone.

        Returns:
            dict: Mapping of zone names to their minimum distance to goal.
        """
        result: Dict[str, float] = {}
        for zone_name in self.graph.zones:
            path_result = self.shortest_path(zone_name, end_name)
            if path_result is None:
                result[zone_name] = float('inf')
            else:
                path, total_cost = path_result
                result[zone_name] = float(total_cost)
        return result

    def _get_closest_unvisited_zone(
            self, distances: Dict[str, float],
            visited: Set[str]) -> Optional[str]:
        """Finds the unvisited zone with the smallest known distance.

        Args:
            distances (dict): Mapping of names to their distance.
            visited (set): Set of zone names already visited.

        Returns:
            str or None: The name of the closest unvisited zone.
        """
        best_zone: Optional[str] = None
        best_dist: float = float('inf')
        for zone, dist in distances.items():
            if zone not in visited and dist < best_dist:
                best_zone = zone
                best_dist = dist
        return best_zone

    def get_neighbour(self, zone_name: str) -> List[str]:
        """Retrieves the names of neighbouring zones for a given zone.

        Args:
            zone_name (str): The name of the zone.

        Returns:
            list: A list of names of connected zones.
        """
        neighbours: List[str] = []
        for connection in self.graph.connections:
            if connection.zone1 == zone_name:
                neighbours.append(connection.zone2)
            if connection.zone2 == zone_name:
                neighbours.append(connection.zone1)
        return neighbours
