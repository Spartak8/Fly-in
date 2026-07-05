class Zone:
    def __init__(self, name, x, y, zone_type="normal", max_drones=1, color=None):
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.max_drones = max_drones
        self.color = color

    def has_capacity(self, current_count):
        return current_count < self.max_drones

    def movement_cost(self):
        if self.zone_type == "blocked":
            return None
        elif self.zone_type == "restricted":
            return 2
        else:
            return 1


class StartHub(Zone):
    def has_capacity(self, current_count):
        return True


class EndHub(Zone):
    def has_capacity(self, current_count):
        return True


class Connection:
    def __init__(self, zone1, zone2, max_link_capacity=1):
        self.zone1 = zone1
        self.zone2 = zone2
        self.max_link_capacity = max_link_capacity


class Drone:
    def __init__(self, drone_id, current_zone, arrived=False):
        self.drone_id = drone_id
        self.current_zone = current_zone
        self.path = []
        self.path_index = 0
        self.arrived = arrived
        self.fly_left = 0
        self.flying_to = None


class Graph:
    def __init__(self):
        self.zones = {}
        self.connections = []

    def add_zone(self, zone: Zone) -> None:
        if zone.name in self.zones:
            raise ValueError(f"Zone {zone.name} already exists")
        self.zones[zone.name] = zone

    def add_connection(self, connection: Connection) -> None:
        self.connections.append(connection)
