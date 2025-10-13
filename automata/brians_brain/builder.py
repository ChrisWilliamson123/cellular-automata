import random

from typing import Callable, List, Tuple

from automata.automaton import Automaton
from automata.brians_brain.brians_brain_automaton import BriansBrainAutomaton
from grid_generator.brians_brain_grid_generator import BriansBrainGridGenerator
from helpers import get_random_odd_number

def brians_brain_automata_from_config(automata: dict, game_size: Tuple[int, int]) -> Callable[[], Automaton]:
    def make_callable(name: str, game_size: Tuple[int, int], grid_configs: dict):
        return lambda: _configged_brians_brain_automaton(name, game_size, grid_configs)

    name = automata['name']
    config = automata['config']
    grid_configs = config['grid_generators']
    return make_callable(name, game_size, grid_configs)

def _configged_brians_brain_automaton(name: str, game_size: Tuple[int, int], grid_configs: dict) -> Automaton:
    grid_generators = []
    for gc in grid_configs:
        initial_size_percentage = gc.get('initial_size_percentage', random.uniform(0.1, 1))
        alive_chance = gc.get('alive_chance', random.uniform(0.2, 0.8))
        center_x, center_y = gc['center']['x'], gc['center']['y']
        center_x = int(center_x * game_size[0])
        center_y = int(center_y * game_size[0])
        center = (center_x, center_y)
        gen = BriansBrainGridGenerator(game_size, initial_size_percentage, center, alive_chance)
        grid_generators.append(gen)
    automaton = BriansBrainAutomaton(grid_generators, name, game_size)
    return automaton
