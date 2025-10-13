import json
from typing import Callable, List, Tuple
import pygame
import random
from automata.automaton import Automaton
from automata.binary_automaton import BinaryAutomaton
from automata.brians_brain_automaton import BriansBrainAutomaton
from automata.cyclic_cellular_automata import CyclicAutomaton, CyclicGridGenerator
from automata.forest_fire_automaton import ForestFireAutomaton, ForestFireGridGenerator
import automata_runner
from grid_generator.binary_grid_generator import BinaryGridGenerator
from grid_generator.brians_brain_grid_generator import BriansBrainGridGenerator
from helpers import get_random_odd_number

def binary_automata_from_config(game_size: Tuple[int, int]) -> List[Callable[[], Automaton]]:
    def make_callable(bs: str, name: str, game_size: Tuple[int, int], grid_configs: dict):
        return lambda: _configged_binary_automaton(bs, name, game_size, grid_configs)

    with open('configs/binary.json', 'r') as f:
        configs = json.load(f)
        callables = []
        for c in configs:
            name = c['name']
            bs = c['bs_notation']
            grid_configs = c['grid_generators']
            callables.append(make_callable(bs, name, game_size, grid_configs))

        return callables

def _configged_binary_automaton(bs_notation: str, name: str, game_size: Tuple[int, int], grid_configs: dict) -> Automaton:
    grid_generators = []
    for gc in grid_configs:
        center_x, center_y = gc['center']['x'], gc['center']['y']
        center_x = int(center_x * game_size[0])
        center_y = int(center_y * game_size[0])
        gen = BinaryGridGenerator(game_size, gc['initial_size'], (center_x, center_y), gc['alive_chance'])
        grid_generators.append(gen)
    automaton = BinaryAutomaton(grid_generators, name, bs_notation, screen_size)
    return automaton

def _binary_automaton(bs_notation: str, name: str, initial_size: int = None, alive_chance: float = None) -> Automaton:
    if not initial_size:    
        lower_grid_bound = 5
        upper_grid_bound = 100
        initial_size = get_random_odd_number(lower_grid_bound, upper_grid_bound)
    if not alive_chance:
        alive_chance = random.uniform(0.3, 0.9)
    grid_generators = [
        # GridGenerator(initial_size, alive_chance, (screen_size[0] / 2, screen_size[1] / 2)),
        BinaryGridGenerator(screen_size, initial_size, (screen_size[0] // 2, screen_size[1] // 2), alive_chance)
    ]
    automaton = BinaryAutomaton(grid_generators, name, bs_notation, screen_size)
    # automata = Automaton(grid_generators, next_state_generator, screen_size, name, f'{bs_notation}, GS: {initial_size}, AC: {alive_chance:.2f}')
    return automaton

def brians_brain() -> Automaton:
    grid_generators = [
        BriansBrainGridGenerator(25, (screen_size[0] / 2, screen_size[1] / 2), 0.45),
    ]
    automaton = BriansBrainAutomaton(grid_generators, 'Brian\'s Brain', screen_size)
    return automaton

def cyclic() -> Automaton:
    number_of_states = 10
    grid_generators = [
        CyclicGridGenerator(screen_size[0] + 1, (screen_size[0] / 2, screen_size[1] / 2), 1, number_of_states),
    ]
    automaton = CyclicAutomaton(grid_generators, 'Cyclic', screen_size, number_of_states)
    return automaton

def forest_fire() -> Automaton:
    grid_generators = [
        # ForestFireGridGenerator(screen_size, screen_size[0] + 1, (screen_size[0] // 2, screen_size[1] // 2), 0.6, 0.00001, 1, 1000, random.randint(1, 5))
        ForestFireGridGenerator(screen_size, screen_size[1] - 1, (screen_size[0] // 2, screen_size[1] // 2), 0.6, 0.00001, 1, 1000, random.randint(1, 5))
    ]
    automaton = ForestFireAutomaton(grid_generators, 'Forest Fire', screen_size)
    return automaton

AUTOMATA_SIZE = (500, 500) # The size that is used to simulate the automata, this is not the final output size.
screen_size = AUTOMATA_SIZE
UPSCALING_FACTOR = 2 # The scaling factor that will be applied to AUTOMATA_SIZE to build the final rendered window size.

# binary_automata = [
#     lambda: binary_automata(AUTOMATA_SIZE),
#     # game_of_life, 
#     # high_life, 
#     # day_and_night, 
#     # seeds, 
#     # life_without_death, 
#     # maze, 
#     # anneal
# ]

binary_automata_callables = binary_automata_from_config(AUTOMATA_SIZE)

# non_binary_automata = [
#     # brians_brain,
#     # cyclic,
#     # forest_fire
# ]

automata_runner.run(AUTOMATA_SIZE, UPSCALING_FACTOR, binary_automata_callables)
