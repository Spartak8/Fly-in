from models import Graph


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
                    pass
                elif key == "end_hub":
                    pass
                elif key == "hub":
                    pass
                elif key == "connection":
                    pass

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
