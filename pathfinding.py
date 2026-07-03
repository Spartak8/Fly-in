from models import Graph, Zone, StartHub, EndHub
from parser import Parser


class Pathfinding:
    def __init__(self, graph):
        self.graph = graph

    def shortest_path(self, start, end):
        distances = {zone: float('inf') for zone in self.graph.zones}
        distances[start] = 0
        previous = {}
        visited = set()
        while True:
            current = self._get_closest_unvisited_zone(distances, visited)
            if current is None:
                break
            if current == end:
                break
            visited.add(current)

            for neighbour in self._get_neighbour(current):
                if neighbour in visited:
                    continue
                neigh = self.graph.zones[neighbour]
                if neigh.movement_cost() is None:
                    continue
                new_distance = distances[current] + neigh.movement_cost()
                if new_distance < distances[neighbour]:
                    distances[neighbour] = new_distance
                    previous[neighbour] = current
        if end not in previous and end != start:
            return None
        total_cost = distances[end]
        path = []
        now = end
        while now != start:
            path.append(now)
            now = previous[now]
        path.append(start)
        path.reverse()
        return path, total_cost

    def _get_closest_unvisited_zone(self, distances, visited):
        best_zone = None
        best_dist = float('inf')
        for zone, dist in distances.items():
            if zone not in visited and dist < best_dist:
                best_zone = zone
                best_dist = dist
        return best_zone

    def _get_neighbour(self, zone_name):
        neighbours = []
        for connection in self.graph.connections:
            if connection.zone1 == zone_name:
                neighbours.append(connection.zone2)
            if connection.zone2 == zone_name:
                neighbours.append(connection.zone1)
        return neighbours


if __name__ == "__main__":
    parser = Parser("maps/easy/01_linear_path.txt")
    nb_drones, graph = parser.parse()

    start_zone = None
    end_zone = None
    for zone in graph.zones.values():
        if isinstance(zone, StartHub):
            start_zone = zone.name
        elif isinstance(zone, EndHub):
            end_zone = zone.name

    pathfind = Pathfinding(graph)
    path, cost = pathfind.shortest_path(start_zone, end_zone)
    print(path)
    print(cost)
