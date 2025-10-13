from enum import Enum
import random
import numpy as np
import pygame
from typing import Annotated, Tuple
from grid_generator.grid_generator import GridGenerator

class BinaryCellState(Enum):
    ALIVE = 1
    DEAD = 0

class BinaryGridGenerator(GridGenerator):
    def __init__(self, screen_size: Tuple[int, int], grid_size: Annotated[int, 'must be an odd number'], center: Tuple[int, int], alive_chance: Annotated[float, 'in range 0...1']):
        super().__init__(screen_size, grid_size, center)

        self.alive_chance = alive_chance
        self.grid_size = grid_size

    def get_cell_state(self, x: int, y: int) -> np.uint8:
        if random.uniform(0, 1) <= self.alive_chance:
            return BinaryCellState.ALIVE.value
        return BinaryCellState.DEAD.value
