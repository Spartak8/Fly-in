import sys
from parser import Parser, ParseError
from simulation import Simulation
from visual import Display


def main() -> None:
    """Main entry point for the simulation program.

    Parses command-line arguments, reads the input map file,
    initializes the simulation, runs it, and displays the results.
    """
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <map_file>")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        parser = Parser(filename)
        nb_drones, graph = parser.parse()
    except ParseError as e:
        print(f"Error parsing map: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"File not found: {filename}")
        sys.exit(1)

    try:
        sim = Simulation(graph, nb_drones)
    except ValueError as e:
        print(f"Simulation error: {e}")
        sys.exit(1)

    turns = sim.run()
    display = Display(turns, graph)
    display.display()
    print(f"\nTotal turns: {len(turns)}")


if __name__ == "__main__":
    main()
