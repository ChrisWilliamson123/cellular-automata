import json
import random

from typing import Callable, List, Tuple

from automata.automaton import Automaton
from automata.binary.binary_automaton import BinaryAutomaton
from grid_generator.binary_grid_generator import BinaryGridGenerator
from helpers import get_random_odd_number

def binary_automata_from_config(automata: dict, game_size: Tuple[int, int]) -> Callable[[], Automaton]:
    def make_callable(bs: str, name: str, game_size: Tuple[int, int], grid_configs: dict):
        return lambda: _configged_binary_automaton(bs, name, game_size, grid_configs)

    name = automata['name']
    config = automata['config']
    bs = config['bs_notation']
    grid_configs = config['grid_generators']
    return make_callable(bs, name, game_size, grid_configs)

def _configged_binary_automaton(bs_notation: str, name: str, game_size: Tuple[int, int], grid_configs: dict) -> Automaton:
    grid_generators = []
    for gc in grid_configs:
        initial_size_percentage = gc.get('initial_size_percentage', random.uniform(0.1, 1))
        alive_chance = gc.get('alive_chance', random.uniform(0.3, 0.9)) 
        center_x, center_y = gc['center']['x'], gc['center']['y']
        center_x = int(center_x * game_size[0])
        center_y = int(center_y * game_size[0])
        gen = BinaryGridGenerator(game_size, initial_size_percentage, (center_x, center_y), alive_chance)
        grid_generators.append(gen)
    automaton = BinaryAutomaton(grid_generators, name, bs_notation, game_size)
    return automaton