from typing import Optional, Dict, List


class Zone:
    """Represents a location or node in the drone graph."""

    def __init__(self, name: str, x: int, y: int,
                 zone_type: str = "normal", max_drones: int = 1,
                 color: Optional[str] = None) -> None:
        """Initializes a Zone.

        Args:
            name (str): The name of the zone.
            x (int): The x-coordinate.
            y (int): The y-coordinate.
            zone_type (str, optional): The type of the zone.
            max_drones (int, optional): The max number of drones allowed.
            color (str, optional): The display color.
        """
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone_type: str = zone_type
        self.max_drones: int = max_drones
        self.color: Optional[str] = color

    def has_capacity(self, current_count: int) -> bool:
        """Checks if the zone has capacity for more drones.

        Args:
            current_count (int): The current number of drones in the zone.

        Returns:
            bool: True if there is capacity, False otherwise.
        """
        return current_count < self.max_drones

    def movement_cost(self) -> Optional[int]:
        """Determines the cost to move into this zone.

        Returns:
            int or None: The cost of moving to the zone, or None if blocked.
        """
        if self.zone_type == "blocked":
            return None
        elif self.zone_type == "restricted":
            return 2
        else:
            return 1


class StartHub(Zone):
    """Represents the starting hub for drones."""

    def has_capacity(self, current_count: int) -> bool:
        """Checks if the start hub has capacity.

        Args:
            current_count (int): The current number of drones in the zone.

        Returns:
            bool: Always True, as start hubs have infinite capacity.
        """
        return True


class EndHub(Zone):
    """Represents the destination hub for drones."""

    def has_capacity(self, current_count: int) -> bool:
        """Checks if the end hub has capacity.

        Args:
            current_count (int): The current number of drones in the zone.

        Returns:
            bool: Always True, as end hubs have infinite capacity.
        """
        return True


class Connection:
    """Represents a connection (edge) between two zones."""

    def __init__(self, zone1: str, zone2: str,
                 max_link_capacity: int = 1) -> None:
        """Initializes a connection.

        Args:
            zone1 (str): The name of the first zone.
            zone2 (str): The name of the second zone.
            max_link_capacity (int, optional): Maximum capacity.
        """
        self.zone1: str = zone1
        self.zone2: str = zone2
        self.max_link_capacity: int = max_link_capacity


class Drone:
    """Represents a drone navigating the graph."""

    def __init__(self, drone_id: int, current_zone: Zone,
                 arrived: bool = False) -> None:
        """Initializes a Drone.

        Args:
            drone_id (int): The unique identifier for the drone.
            current_zone (Zone): The zone where the drone is currently located.
            arrived (bool, optional): Whether the drone has reached its goal.
        """
        self.drone_id: int = drone_id
        self.current_zone: Zone = current_zone
        self.arrived: bool = arrived
        self.fly_left: int = 0
        self.flying_to: Optional[str] = None
        self.using_connection: Optional[Connection] = None


class Graph:
    """Represents the network graph of zones and connections."""

    def __init__(self) -> None:
        """Initializes an empty Graph."""
        self.zones: Dict[str, Zone] = {}
        self.connections: List[Connection] = []

    def add_zone(self, zone: Zone) -> None:
        """Adds a zone to the graph.

        Args:
            zone (Zone): The zone object to add.

        Raises:
            ValueError: If a zone with the same name already exists.
        """
        if zone.name in self.zones:
            raise ValueError(f"Zone {zone.name} already exists")
        self.zones[zone.name] = zone

    def add_connection(self, connection: Connection) -> None:
        """Adds a connection to the graph.

        Args:
            connection (Connection): The connection object to add.
        """
        self.connections.append(connection)
