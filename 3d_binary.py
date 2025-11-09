# A headless runner which renders a single automaton
import json
import random
from typing import Tuple

from automata.automaton import Automaton
from automata.binary.builder import binary_automata_from_config
from automata.brians_brain.builder import brians_brain_automata_from_config
from automata.forest_fire.builder import forest_fire_automata_from_config
from automata.binary_3d.binary_3d_automaton import Binary3dAutomaton
from automata.binary_3d.binary_3d_grid_generator import Binary3dGridGenerator
from runners import headless_runner

# with open('configs/automata.json') as f:
#     configs = json.load(f)

# builder_map = {
#     'binary': binary_automata_from_config,
#     'forest-fire': forest_fire_automata_from_config,
#     'brians-brain': brians_brain_automata_from_config
# }

# automaton_size = (300, 300)

# gol_config = list(filter(lambda c: c['name'] == 'Game of Life', configs))[0]
# gol = binary_automata_from_config(gol_config, automaton_size)

def _configged_binary_automaton(bs_notation: str, name: str, game_size: Tuple[int, int], grid_configs: dict) -> Automaton:
    grid_generators = []
    for gc in grid_configs:
        # initial_size_percentage = gc.get('initial_size_percentage', random.uniform(0.1, 1))
        initial_size_percentage = 0.1
        alive_chance = gc.get('alive_chance', random.uniform(0.3, 0.9)) 
        center_x, center_y = gc['center']['x'], gc['center']['y']
        center_x = int(center_x * game_size[0])
        center_y = int(center_y * game_size[0])
        gen = Binary3dGridGenerator(game_size, initial_size_percentage, (center_x, center_y), alive_chance)
        grid_generators.append(gen)
    automaton = Binary3dAutomaton(grid_generators, name, bs_notation, game_size)
    return automaton
headless_runner.run(lambda: _configged_binary_automaton('B1/S1', '3D', (75, 75), [{'center': {'x': 0.5, 'y': 0.5}}]))
