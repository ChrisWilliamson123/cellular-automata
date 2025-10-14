# A headless runner which renders a single automaton
import json

from automata.binary.builder import binary_automata_from_config
from automata.brians_brain.builder import brians_brain_automata_from_config
from automata.forest_fire.builder import forest_fire_automata_from_config
from runners import headless_runner

with open('configs/automata.json') as f:
    configs = json.load(f)

builder_map = {
    'binary': binary_automata_from_config,
    'forest-fire': forest_fire_automata_from_config,
    'brians-brain': brians_brain_automata_from_config
}

automaton_size = (300, 300)

gol_config = list(filter(lambda c: c['name'] == 'Game of Life', configs))[0]
gol = binary_automata_from_config(gol_config, automaton_size)
headless_runner.run(gol)
