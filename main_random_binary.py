import random

from typing import Callable, List

from automata.automaton import Automaton
from automata.binary.binary_automaton import BinaryAutomaton
from automata.binary.builder import binary_automata_from_config
import runners.automata_runner as automata_runner
from grid_generator.binary_grid_generator import BinaryGridGenerator

def random_bs_notation() -> str:
    """
    Generate a random binary cellular automaton rule in B/S notation.
    Example: 'B3/S23' (Conway's Game of Life)
    """
    # Pick random subsets of [0..8] for birth and survival
    birth = sorted(random.sample(range(1, 9), random.randint(1, 8)))
    survival = sorted(random.sample(range(0, 9), random.randint(0, 9)))

    # Convert to string form
    b_str = ''.join(map(str, birth))
    s_str = ''.join(map(str, survival))

    return f"B{b_str}/S{s_str}"

AUTOMATA_SIZE = (500, 500) # The size that is used to simulate the automata, this is not the final output size.
game_size = AUTOMATA_SIZE
UPSCALING_FACTOR = 2 # The scaling factor that will be applied to AUTOMATA_SIZE to build the final rendered window size.

builder_map = {
    'binary': binary_automata_from_config,
}

# def build_automata():
#     initial_size_percentage = random.uniform(0.05, 0.8)
#     alive_chance = random.uniform(0.01, 0.75)
#     center_x, center_y = 0.5, 0.5
#     center_x = int(center_x * game_size[0])
#     center_y = int(center_y * game_size[0])
#     gen = BinaryGridGenerator(game_size, initial_size_percentage, (center_x, center_y), alive_chance)
#     # notation = random_bs_notation()
#     notation = 'B345678/S46'
#     print(initial_size_percentage, alive_chance)
#     automaton = BinaryAutomaton([gen], 'Random', notation, game_size)
#     return automaton

def build_automata():
    initial_size_percentage = 1
    alive_chance = 0.15
    center_x, center_y = 0.5, 0.5
    center_x = int(center_x * game_size[0])
    center_y = int(center_y * game_size[0])
    gen = BinaryGridGenerator(game_size, initial_size_percentage, (center_x, center_y), alive_chance)
    # notation = random_bs_notation()
    notation = 'B345678/S46'
    print(initial_size_percentage, alive_chance)
    automaton = BinaryAutomaton([gen], 'Random', notation, game_size)
    return automaton

automata_runner.run(AUTOMATA_SIZE, UPSCALING_FACTOR, [build_automata])

# Cool ones
'B345678/S46', 0.60, 0.21 # Not, size, alive
