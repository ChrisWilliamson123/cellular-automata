import random

from typing import Callable, List, Tuple

from automata.automaton import Automaton
from automata.forest_fire.forest_fire_automaton import ForestFireAutomaton, ForestFireGridGenerator
from helpers import get_random_odd_number

def forest_fire_automata_from_config(automata: dict, game_size: Tuple[int, int]) -> Callable[[], Automaton]:
    def make_callable(name: str, game_size: Tuple[int, int], grid_configs: dict):
        return lambda: _configged_forest_fire_automaton(name, game_size, grid_configs)

    name = automata['name']
    config = automata['config']
    grid_configs = config['grid_generators']
    return make_callable(name, game_size, grid_configs)

def _configged_forest_fire_automaton(name: str, game_size: Tuple[int, int], grid_configs: dict) -> Automaton:
    grid_generators = []
    for gc in grid_configs:
        initial_size = gc.get('initial_size', get_random_odd_number(5, game_size[1] // 4))
        tree_chance = gc.get('tree_chance', random.uniform(0.5, 1))
        burning_chance = gc.get('burning_chance', random.uniform(0.00001, 0.0001))
        lake_chance = gc.get('lake_chance', random.uniform(0, 1))
        lake_size = gc.get('lake_size', random.uniform(100, 1000))
        lake_amount = gc.get('lake_amount', random.randint(1, 5))
        center_x, center_y = gc['center']['x'], gc['center']['y']
        center_x = int(center_x * game_size[0])
        center_y = int(center_y * game_size[0])
        center = (center_x, center_y)
        gen = ForestFireGridGenerator(game_size, initial_size, center, tree_chance, burning_chance, lake_chance, lake_size, lake_amount)
        grid_generators.append(gen)
    automaton = ForestFireAutomaton(grid_generators, name, game_size)
    return automaton
