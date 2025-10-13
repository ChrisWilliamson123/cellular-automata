import json
from typing import Callable, List, Tuple
import pygame
import random
from automata.automaton import Automaton
from automata.binary.builder import binary_automata_from_config
from automata.brians_brain_automaton import BriansBrainAutomaton
from automata.cyclic_cellular_automata import CyclicAutomaton, CyclicGridGenerator
from automata.forest_fire.builder import forest_fire_automata_from_config
import automata_runner
from grid_generator.binary_grid_generator import BinaryGridGenerator
from grid_generator.brians_brain_grid_generator import BriansBrainGridGenerator
from helpers import get_random_odd_number

# def brians_brain() -> Automaton:
#     grid_generators = [
#         BriansBrainGridGenerator(25, (screen_size[0] / 2, screen_size[1] / 2), 0.45),
#     ]
#     automaton = BriansBrainAutomaton(grid_generators, 'Brian\'s Brain', screen_size)
#     return automaton
# 
# def cyclic() -> Automaton:
#     number_of_states = 10
#     grid_generators = [
#         CyclicGridGenerator(screen_size[0] + 1, (screen_size[0] / 2, screen_size[1] / 2), 1, number_of_states),
#     ]
#     automaton = CyclicAutomaton(grid_generators, 'Cyclic', screen_size, number_of_states)
#     return automaton
# 
# def forest_fire() -> Automaton:
#     grid_generators = [
#         # ForestFireGridGenerator(screen_size, screen_size[0] + 1, (screen_size[0] // 2, screen_size[1] // 2), 0.6, 0.00001, 1, 1000, random.randint(1, 5))
#         ForestFireGridGenerator(screen_size, screen_size[1] - 1, (screen_size[0] // 2, screen_size[1] // 2), 0.6, 0.00001, 1, 1000, random.randint(1, 5))
#     ]
#     automaton = ForestFireAutomaton(grid_generators, 'Forest Fire', screen_size)
#     return automaton

AUTOMATA_SIZE = (500, 500) # The size that is used to simulate the automata, this is not the final output size.
game_size = AUTOMATA_SIZE
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

with open('configs/automata.json') as f:
    configs = json.load(f)

builder_map = {
    'binary': binary_automata_from_config,
    'forest-fire': forest_fire_automata_from_config
}

callables: List[Callable[[], Automaton]] = []
for automata in configs:
    callables.append(builder_map[automata['type']](automata, game_size))

automata_runner.run(AUTOMATA_SIZE, UPSCALING_FACTOR, callables)
