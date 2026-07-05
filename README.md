*This project has been created as part of the 42 curriculum by skhachat.*

# Fly-in: Drone Network Simulation

## Description

**Fly-in** is a terminal-based simulation and pathfinding application designed to model the navigation of a swarm of drones through a complex network of hubs and zones. 

The goal of this project is to efficiently route a specified number of drones from a starting hub (`StartHub`) to a destination hub (`EndHub`) while respecting various constraints. The graph is composed of zones with varying movement costs (e.g., normal, restricted, blocked) and limited capacities (maximum number of drones allowed simultaneously). Connections between zones also have maximum link capacities. The simulation calculates the optimal path for each drone and visualizes their step-by-step movement until all drones have safely arrived at their destination.

## Instructions

### Prerequisites
- Python 3.8+
- The required dependencies can be installed using the provided `Makefile`.

### Installation
Clone the repository and install any necessary requirements:
```bash
make install
```

### Execution
To run the simulation, use the `main.py` script and pass a map file as an argument:
```bash
python3 main.py maps/challenger/01_the_impossible_dream.txt
```
Alternatively, you can use the `Makefile`:
```bash
make run ARGS="maps/challenger/01_the_impossible_dream.txt"
```

### Linting and Code Quality
This project adheres to strict PEP-8 standards and utilizes static typing. You can run the linters with:
```bash
make lint
# or
make lint-strict
```

## Algorithm Choices and Implementation Strategy

### Pathfinding Strategy
The core pathfinding relies on **Dijkstra's Algorithm**. Instead of calculating a path for each drone individually on every step, the `Pathfinding` class calculates the shortest distance from *all* zones to the `EndHub` at the beginning of the simulation (`distances_to_goal`). 

This approach uses a reverse-search strategy where the cost to reach the destination from any adjacent node is known. It takes into account the `movement_cost` of different zone types (e.g., restricted zones cost 2 points, blocked zones are ignored). 

### Simulation Logic
During the simulation (`simulation.py`), drones use a greedy approach combined with capacity constraints:
1. **Distance Minimization:** Drones evaluate all neighboring zones and prioritize those that have a shorter distance to the `EndHub` than their current zone.
2. **Capacity Checks:** Before moving, the simulation verifies if the chosen neighbor has available capacity (`max_drones`) and if the connection link has not exceeded its `max_link_capacity`.
3. **Turn-based Advancement:** Drones require a specific number of turns to traverse restricted zones. The `_advance_drone` logic tracks the remaining fly time (`fly_left`) for each drone and locks the capacity until the drone has fully arrived at the next node.

This strategy ensures that drones don't just blindly follow the absolute shortest path and get deadlocked; they respect physical space and connection bandwidth constraints dynamically per turn.

## Visual Representation Features

The project includes a terminal-based visualizer (`visual.py`) that significantly enhances the user experience. 

- **ANSI Color Coding:** Zones are assigned specific colors via the map metadata. The visualizer reads these colors and applies standard ANSI color codes to the terminal output.
- **Dynamic Legend:** A legend is generated at the start of the simulation output, mapping each colored zone name to its specific type (`normal`, `restricted`, `blocked`, etc.).
- **Movement Tracking:** During the simulation, the output displays each drone's movement per turn (e.g., `D1-ZoneA`). The zone name is colorized according to its attributes. 

This visual representation allows users to quickly track drone swarms at a glance, instantly recognize bottlenecks (e.g., a cluster of drones waiting at a red restricted zone), and verify the correctness of the pathfinding logic without having to read raw text coordinates.

## Resources

- **Dijkstra's Algorithm:** [Wikipedia - Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- **Python Typing Documentation:** [PEP 484 – Type Hints](https://peps.python.org/pep-0484/)
- **ANSI Escape Codes:** [ANSI colors in terminal](https://en.wikipedia.org/wiki/ANSI_escape_code)

### AI Usage
Artificial Intelligence (LLM) was utilized during the development of this project to improve code quality and documentation. Specifically:
- **Code Refactoring:** AI was used to enforce strict PEP-8 compliance (`flake8`) and add comprehensive static type hinting across all Python files to pass `mypy --strict`.
- **Documentation:** AI generated the Google-style standard docstrings for all classes and methods to ensure the codebase remains maintainable and easily understandable.
- **README Generation:** AI was used to draft and structure this `README.md` document based on the project's source code and the specific curriculum requirements.
