from typing import Tuple, Dict
from models import Graph, StartHub, EndHub, Zone, Connection


class ParseError(Exception):
    """Custom exception raised for errors encountered during map parsing."""

    def __init__(self, line_number: int, message: str) -> None:
        """Initializes the ParseError.

        Args:
            line_number (int): The line number where the error occurred.
            message (str): A description of the error.
        """
        self.line_number: int = line_number
        self.message: str = message
        super().__init__(f"Error on line {line_number}: {message}")


class Parser:
    """Parses a map file to extract drones count and graph layout."""

    def __init__(self, filename: str) -> None:
        """Initializes the Parser.

        Args:
            filename (str): The path to the map file.
        """
        self.filename: str = filename

    def parse(self) -> Tuple[int, Graph]:
        """Parses the given map file and constructs the network graph.

        Returns:
            tuple: Number of drones (int) and the parsed Graph object.

        Raises:
            ParseError: If file format is invalid, or missing elements.
        """
        nb_drones: int = 0
        line_number: int = 0
        start_hub_count: int = 0
        end_hub_count: int = 0
        graph: Graph = Graph()
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
                        raise ParseError(line_number, "must be a single value")
                    try:
                        nb_drones = int(parts[0])
                    except ValueError:
                        raise ParseError(line_number, "must be an integer")
                    if nb_drones <= 0:
                        raise ParseError(line_number, "must be positive")
                elif key == "start_hub":
                    start_hub_count += 1
                    if start_hub_count > 1:
                        raise ParseError(line_number, "only one is allowed")
                    name, x, y, metadata = self._parse_zone(value, line_number)
                    try:
                        max_drones = int(metadata.get("max_drones", "1"))
                    except ValueError:
                        raise ParseError(line_number, "must be an integer")
                    if max_drones <= 0:
                        raise ParseError(line_number, "must be positive")
                    allowed_zone_types = {
                        "normal", "blocked", "restricted", "priority"
                    }
                    zone_type = metadata.get("zone", "normal")
                    if zone_type not in allowed_zone_types:
                        raise ParseError(
                            line_number, f"invalid type '{zone_type}'")
                    zone_s = StartHub(name, x, y,
                                      zone_type=zone_type,
                                      color=metadata.get("color"),
                                      max_drones=max_drones)
                    try:
                        graph.add_zone(zone_s)
                    except ValueError as e:
                        raise ParseError(line_number, str(e))
                elif key == "end_hub":
                    end_hub_count += 1
                    if end_hub_count > 1:
                        raise ParseError(line_number, "only one is allowed")
                    name, x, y, metadata = self._parse_zone(value, line_number)
                    try:
                        max_drones = int(metadata.get("max_drones", "1"))
                    except ValueError:
                        raise ParseError(line_number, "must be an integer")
                    if max_drones <= 0:
                        raise ParseError(line_number, "must be positive")
                    allowed_zone_types = {
                        "normal", "blocked", "restricted", "priority"
                    }
                    zone_type = metadata.get("zone", "normal")
                    if zone_type not in allowed_zone_types:
                        raise ParseError(
                            line_number, f"invalid type '{zone_type}'")
                    zone_e = EndHub(name, x, y,
                                    zone_type=zone_type,
                                    color=metadata.get("color"),
                                    max_drones=max_drones)
                    try:
                        graph.add_zone(zone_e)
                    except ValueError as e:
                        raise ParseError(line_number, str(e))
                elif key == "hub":
                    name, x, y, metadata = self._parse_zone(value, line_number)
                    try:
                        max_drones = int(metadata.get("max_drones", "1"))
                    except ValueError:
                        raise ParseError(line_number, "must be an integer")
                    if max_drones <= 0:
                        raise ParseError(line_number, "must be positive")
                    allowed_zone_types = {
                        "normal", "blocked", "restricted", "priority"
                    }
                    zone_type = metadata.get("zone", "normal")
                    if zone_type not in allowed_zone_types:
                        raise ParseError(
                            line_number, f"invalid type '{zone_type}'")
                    zone = Zone(name, x, y,
                                zone_type=zone_type,
                                color=metadata.get("color"),
                                max_drones=max_drones)
                    try:
                        graph.add_zone(zone)
                    except ValueError as e:
                        raise ParseError(line_number, str(e))
                elif key == "connection":
                    zone1, zone2, conn_meta = self._parse_connection(
                        value, line_number)
                    if zone1 not in graph.zones or zone2 not in graph.zones:
                        raise ParseError(line_number, "zone not found")
                    try:
                        max_link_cap = int(
                            conn_meta.get("max_link_capacity", "1"))
                    except ValueError:
                        raise ParseError(line_number, "must be an integer")
                    if max_link_cap <= 0:
                        raise ParseError(line_number, "must be positive")
                    for graph1 in graph.connections:
                        if graph1.zone1 == zone1 and graph1.zone2 == zone2:
                            raise ParseError(line_number, "already exists")
                        if graph1.zone1 == zone2 and graph1.zone2 == zone1:
                            raise ParseError(line_number, "already exists")
                    graph.add_connection(
                        Connection(zone1, zone2, max_link_cap))
        if nb_drones == 0:
            raise ParseError(line_number, "no nb_drones defined in file")
        if start_hub_count == 0:
            raise ParseError(line_number, "no start_hub defined in file")
        if end_hub_count == 0:
            raise ParseError(line_number, "no end_hub defined in file")
        return nb_drones, graph

    def _parse_zone(self, value: str,
                    line_number: int) -> Tuple[str, int, int, Dict[str, str]]:
        """Parses a zone configuration string.

        Args:
            value (str): The value part of the line defining the zone.
            line_number (int): The current line number being parsed.

        Returns:
            tuple: Zone name (str), x (int), y (int), and metadata (dict).

        Raises:
            ParseError: If the zone definition format is invalid.
        """
        parts = value.split()
        if len(parts) < 3:
            raise ParseError(line_number, "must have at least 3 values")
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
            metadata: Dict[str, str] = {}
            for pair in pairs:
                kv = pair.split("=")
                if len(kv) != 2:
                    raise ParseError(line_number, f"Invalid pair: {pair}")
                metadata[kv[0]] = kv[1]
            return name, x, y, metadata

    def _parse_connection(
            self, value: str,
            line_number: int) -> Tuple[str, str, Dict[str, str]]:
        """Parses a connection configuration string.

        Args:
            value (str): The value part of the line defining the connection.
            line_number (int): The current line number being parsed.

        Returns:
            tuple: First zone name, second zone name, and metadata (dict).

        Raises:
            ParseError: If the connection definition format is invalid.
        """
        parts = value.split()
        if len(parts) < 1:
            raise ParseError(line_number, "missing zone names")
        name_parts = parts[0].split("-")
        if len(name_parts) != 2:
            raise ParseError(line_number, f"invalid format: {parts[0]}")
        zone1, zone2 = name_parts
        metadata_parts = " ".join(parts[1:])
        if metadata_parts == "":
            return zone1, zone2, {}
        else:
            pairs = metadata_parts.strip("[]").split()
            metadata: Dict[str, str] = {}
            for pair in pairs:
                kv = pair.split("=")
                if len(kv) != 2:
                    raise ParseError(line_number, f"Invalid pair: {pair}")
                metadata[kv[0]] = kv[1]
            return zone1, zone2, metadata
