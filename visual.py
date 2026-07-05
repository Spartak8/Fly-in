from typing import List, Dict
from simulation import Simulation
from models import Graph


class Display():
    """Handles the terminal-based visual output of the simulation."""

    def __init__(self, simulation: List[List[str]], graph: Graph) -> None:
        """Initializes the Display.

        Args:
            simulation (list): The list of turns, with movement strings.
            graph (Graph): The network graph containing zones.
        """
        self.simulation: List[List[str]] = simulation
        self.graph: Graph = graph
        self.colors: Dict[str, str] = {
            "red": "\033[91m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "purple": "\033[95m",
            "cyan": "\033[96m",
            "gray": "\033[90m",
            "orange": "\033[93m",
            "maroon": "\033[91m",
            "gold": "\033[93m",
            "violet": "\033[95m",
            "crimson": "\033[91m",
            "black": "\033[90m",
            "darkred": "\033[91m",
            "brown": "\033[33m",
        }
        self.reset: str = "\033[0m"

    def _colorize(self, text: str, color_name: str | None) -> str:
        """Applies ANSI color codes to the given text.

        Args:
            text (str): The text to colorize.
            color_name (str): The name of the color to apply.

        Returns:
            str: The colorized string, or original if color not found.
        """
        if color_name is None:
            return text
        code = self.colors.get(color_name, "")
        if not code:
            return text
        return f"{code}{text}{self.reset}"

    def _build_legend(self) -> List[str]:
        """Builds a legend representing all zones and their types.

        Returns:
            list: A list of formatted string lines for the legend.
        """
        lines: List[str] = []
        for zone in self.graph.zones.values():
            line = self._colorize(zone.name, zone.color)
            lines.append(f"{line}: {zone.zone_type}")
        return lines

    def _colorize_moves(self) -> List[List[str]]:
        """Colorizes the movements of drones based on the zone colors.

        Returns:
            list: A new list of turns with colorized output strings.
        """
        result: List[List[str]] = []
        for turn in self.simulation:
            colored_turn: List[str] = []
            for move in turn:
                parts = move.split("-")
                drone = parts[0]
                zone_part = "-".join(parts[1:])
                last_zone = parts[-1]
                zone = self.graph.zones[last_zone]
                colored_zone = self._colorize(zone_part, zone.color)
                colored_turn.append(f"{drone}-{colored_zone}")
            result.append(colored_turn)
        return result

    def display(self) -> None:
        """Prints the legend and the full simulation to standard output."""
        legend = self._build_legend()
        colored_turns = self._colorize_moves()
        print("\n".join(legend))
        print()
        for turn in colored_turns:
            print(" ".join(turn))


if __name__ == "__main__":
    from parser import Parser

    parser = Parser("maps/challenger/01_the_impossible_dream.txt")
    parsed_nb_drones, parsed_graph = parser.parse()

    sim = Simulation(parsed_graph, parsed_nb_drones)
    res_turns = sim.run()

    display = Display(res_turns, parsed_graph)
    display.display()
    print(f"\nTotal turns: {len(res_turns)}")
