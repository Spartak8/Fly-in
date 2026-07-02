from models import Graph, StartHub, EndHub, Zone, Connection


class ParseError(Exception):
    def __init__(self, line_number, message):
        self.line_number = line_number
        self.message = message
        super().__init__(f"Error on line {line_number}: {message}")


class Parser:
    def __init__(self, filename):
        self.filename = filename

    def parse(self):
        nb_drones = 0
        line_number = 0
        start_hub_count = 0
        end_hub_count = 0
        graph = Graph()
        with open(self.filename) as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if ":" not in line:
                    raise ParseError(line_number, "Invalid line: missing :")
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                if key == "nb_drones":
                    parts = value.split()
                    if len(parts) != 1:
                        raise ParseError(line_number, "nb_drones must be a single value")
                    try:
                        nb_drones = int(parts[0])
                    except ValueError:
                        raise ParseError(line_number, "nb_drones must be an integer")
                    if nb_drones <= 0:
                        raise ParseError(line_number, "nb_drones must be a positive integer")
                elif key == "start_hub":
                    start_hub_count += 1
                    if start_hub_count > 1:
                        raise ParseError(line_number, "only one start_hub is allowed")
                    name, x, y, metadata = self._parse_zone(value, line_number)
                    try:
                        max_drones = int(metadata.get("max_drones", 1))
                    except ValueError:
                        raise ParseError(line_number, "max_drones must be an integer")
                    if max_drones <= 0:
                        raise ParseError(line_number, "max_drones must be a positive integer")
                    allowed_zone_types = {"normal", "blocked", "restricted", "priority"}
                    zone_type = metadata.get("zone", "normal")
                    if zone_type not in allowed_zone_types:
                        raise ParseError(line_number, f"invalid zone type '{zone_type}'")
                    zone = StartHub(name, x, y,
                                    zone_type=zone_type,
                                    color=metadata.get("color"),
                                    max_drones=max_drones)
                    try:
                        graph.add_zone(zone)
                    except ValueError as e:
                        raise ParseError(line_number, str(e))
                elif key == "end_hub":
                    end_hub_count += 1
                    if end_hub_count > 1:
                        raise ParseError(line_number, "only one end_hub is allowed")
                    name, x, y, metadata = self._parse_zone(value, line_number)
                    try:
                        max_drones = int(metadata.get("max_drones", 1))
                    except ValueError:
                        raise ParseError(line_number, "max_drones must be an integer")
                    if max_drones <= 0:
                        raise ParseError(line_number, "max_drones must be a positive integer")
                    allowed_zone_types = {"normal", "blocked", "restricted", "priority"}
                    zone_type = metadata.get("zone", "normal")
                    if zone_type not in allowed_zone_types:
                        raise ParseError(line_number, f"invalid zone type '{zone_type}'")
                    zone = EndHub(name, x, y,
                                  zone_type=zone_type,
                                  color=metadata.get("color"),
                                  max_drones=max_drones)
                    try:
                        graph.add_zone(zone)
                    except ValueError as e:
                        raise ParseError(line_number, str(e))
                elif key == "hub":
                    name, x, y, metadata = self._parse_zone(value, line_number)
                    try:
                        max_drones = int(metadata.get("max_drones", 1))
                    except ValueError:
                        raise ParseError(line_number, "max_drones must be an integer")
                    if max_drones <= 0:
                        raise ParseError(line_number, "max_drones must be a positive integer")
                    allowed_zone_types = {"normal", "blocked", "restricted", "priority"}
                    zone_type = metadata.get("zone", "normal")
                    if zone_type not in allowed_zone_types:
                        raise ParseError(line_number, f"invalid zone type '{zone_type}'")
                    zone = Zone(name, x, y,
                                zone_type=zone_type,
                                color=metadata.get("color"),
                                max_drones=max_drones)
                    try:
                        graph.add_zone(zone)
                    except ValueError as e:
                        raise ParseError(line_number, str(e))
                elif key == "connection":
                    zone1, zone2, metadata = self._parse_connection(value, line_number)
                    if zone1 not in graph.zones or zone2 not in graph.zones:
                        raise ParseError(line_number, "zone not found")
                    try:
                        max_link_capacity = int(metadata.get("max_link_capacity", 1))
                    except ValueError:
                        raise ParseError(line_number, "max_link_capacity must be an integer")
                    if max_link_capacity <= 0:
                        raise ParseError(line_number, "max_link_capacity must be a positive integer")
                    for graph1 in graph.connections:
                        if graph1.zone1 == zone1 and graph1.zone2 == zone2:
                            raise ParseError(line_number, "connection already exists")
                        if graph1.zone1 == zone2 and graph1.zone2 == zone1:
                            raise ParseError(line_number, "connection already exists")
                    graph.add_connection(Connection(zone1, zone2, max_link_capacity))
        if start_hub_count == 0:
            raise ParseError(line_number, "no start_hub defined in file")
        if end_hub_count == 0:
            raise ParseError(line_number, "no end_hub defined in file")
        return nb_drones, graph

    def _parse_zone(self, value, line_number):
        parts = value.split()
        if len(parts) < 3:
            raise ParseError(line_number, "zone must have at least 3 values (name, x, y)")
        name = parts[0]
        try:
            x = int(parts[1])
            y = int(parts[2])
        except ValueError:
            raise ParseError(line_number, "x and y must be integers")
        metadata_parts = " ".join(parts[3:])
        if metadata_parts == "":
            return name, x, y, {}
        else:
            pairs = metadata_parts.strip("[]").split()
            metadata = {}
            for pair in pairs:
                kv = pair.split("=")
                if len(kv) != 2:
                    raise ParseError(line_number, f"Invalid metadata pair: {pair}")
                metadata[kv[0]] = kv[1]
            return name, x, y, metadata
    
    def _parse_connection(self, value, line_number):
        parts = value.split()
        if len(parts) < 1:
            raise ParseError(line_number, "connection line is missing zone names")
        name_parts = parts[0].split("-")
        if len(name_parts) != 2:
            raise ParseError(line_number, f"invalid connection format: {parts[0]}")
        zone1, zone2 = name_parts
        metadata_parts = " ".join(parts[1:])
        if metadata_parts == "":
            return zone1, zone2, {}
        else:
            pairs = metadata_parts.strip("[]").split()
            metadata = {}
            for pair in pairs:
                kv = pair.split("=")
                if len(kv) != 2:
                    raise ParseError(line_number, f"Invalid metadata pair: {pair}")
                metadata[kv[0]] = kv[1]
            return zone1, zone2, metadata


if __name__ == "__main__":
    parser = Parser("maps/challenger/01_the_impossible_dream.txt")
    try:
        nb_drones, graph = parser.parse()
        print(nb_drones)
        for zone in graph.zones.values():
            print(zone.name, zone.x, zone.y, zone.zone_type, zone.color, zone.max_drones)
        for connection in graph.connections:
            print(connection.zone1, connection.zone2, connection.max_link_capacity)
    except ParseError as e:
        print(e)
