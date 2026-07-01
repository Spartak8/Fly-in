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
                    name, x, y, metadata = self._parse_zone(value, line_number)
                    try:
                        max_drones = int(metadata.get("max_drones", 1))
                    except ValueError:
                        raise ParseError(line_number, "max_drones must be an integer")
                    zone = StartHub(name, x, y,
                                    zone_type=metadata.get("zone", "normal"),
                                    color=metadata.get("color"),
                                    max_drones=max_drones)
                    graph.add_zone(zone)
                elif key == "end_hub":
                    name, x, y, metadata = self._parse_zone(value, line_number)
                    try:
                        max_drones = int(metadata.get("max_drones", 1))
                    except ValueError:
                        raise ParseError(line_number, "max_drones must be an integer")
                    zone = EndHub(name, x, y,
                                  zone_type=metadata.get("zone", "normal"),
                                  color=metadata.get("color"),
                                  max_drones=max_drones)
                    graph.add_zone(zone)
                elif key == "hub":
                    name, x, y, metadata = self._parse_zone(value, line_number)
                    try:
                        max_drones = int(metadata.get("max_drones", 1))
                    except ValueError:
                        raise ParseError(line_number, "max_drones must be an integer")
                    zone = Zone(name, x, y,
                                zone_type=metadata.get("zone", "normal"),
                                color=metadata.get("color"),
                                max_drones=max_drones)
                    graph.add_zone(zone)
                elif key == "connection":
                    zone1, zone2, metadata = self._parse_connection(value, line_number)
                    if zone1 not in graph.zones or zone2 not in graph.zones:
                        raise ParseError(line_number, "zone not found")
                    try:
                        max_link_capacity = int(metadata.get("max_link_capacity", 1))
                    except ValueError:
                        raise ParseError(line_number, "max_link_capacity must be an integer")
                    for graph1 in graph.connections:
                        if graph1.zone1 == zone1 and graph1.zone2 == zone2:
                            raise ParseError(line_number, "connection already exists")
                        if graph1.zone1 == zone2 and graph1.zone2 == zone1:
                            raise ParseError(line_number, "connection already exists")
                    graph.add_connection(Connection(zone1, zone2, max_link_capacity))
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
