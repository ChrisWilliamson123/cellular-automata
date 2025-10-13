from enum import Enum
import random
from typing import Annotated, Tuple
from automata.brians_brain_automaton import BriansBrainCellState
from grid_generator.grid_generator import GridGenerator

class BriansBrainGridGenerator(GridGenerator):
    def __init__(self, grid_size: Annotated[int, 'must be an odd number'], center: Tuple[int, int], alive_chance: Annotated[float, 'in range 0...1']):
        super().__init__(grid_size, center)

        self.alive_chance = alive_chance
        self.grid_size = grid_size

    def get_cell_state(self, x: int, y: int) -> BriansBrainCellState:
        if random.uniform(0, 1) <= self.alive_chance:
            return BriansBrainCellState.ALIVE
