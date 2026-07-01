class Zone:
    def __init__(self, name, x, y, zone_type="normal", max_drones=1, color=None):
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.max_drones = max_drones
        self.color = color


class StartHub(Zone):
    pass


class EndHub(Zone):
    pass


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
        self.arrived = arrived


class Graph:
    def __init__(self):
        self.zones = {}
        self.connections = []

    def add_zone(self, zone):
        self.zones[zone.name] = zone

    def add_connection(self, connection):
        self.connections.append(connection)
