import json
from typing import Callable, List
from automata.automaton import Automaton
from automata.binary.builder import binary_automata_from_config
from automata.brians_brain.builder import brians_brain_automata_from_config
from automata.forest_fire.builder import forest_fire_automata_from_config
import runners.automata_runner as automata_runner

AUTOMATA_SIZE = (100, 100) # The size that is used to simulate the automata, this is not the final output size.
game_size = AUTOMATA_SIZE
UPSCALING_FACTOR = 1 # The scaling factor that will be applied to AUTOMATA_SIZE to build the final rendered window size.

with open('configs/automata.json') as f:
    configs = json.load(f)

builder_map = {
    'binary': binary_automata_from_config,
    'forest-fire': forest_fire_automata_from_config,
    'brians-brain': brians_brain_automata_from_config
}

callables: List[Callable[[], Automaton]] = []
for automata in configs:
    callables.append(builder_map[automata['type']](automata, game_size))

automata_runner.run(AUTOMATA_SIZE, UPSCALING_FACTOR, callables, show_text_overlays=False, framerate=30)
