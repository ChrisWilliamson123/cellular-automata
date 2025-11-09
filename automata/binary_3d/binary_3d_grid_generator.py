from enum import Enum
import random
import numpy as np
import numpy.typing as npt
from typing import Annotated, Tuple
from grid_generator.grid_generator import GridGenerator

class BinaryCellState(Enum):
    ALIVE = 1
    DEAD = 0

class Binary3dGridGenerator():
    def __init__(self, screen_size: Tuple[int, int], grid_size_percentage: int, center: Tuple[int, int], alive_chance: float):
        self.alive_chance = alive_chance
        self.screen_size = screen_size
        self.grid_size_percentage = grid_size_percentage
        self.center = center
        width = int(self.screen_size[0] * self.grid_size_percentage)
        if width % 2 == 0:
            width -= 1
        height = int(self.screen_size[1] * self.grid_size_percentage)
        if height % 2 == 0:
            height -= 1
        depth = int(self.screen_size[0] * self.grid_size_percentage)
        if depth % 2 == 0:
            depth -= 1
        self.grid_size = (width, height, depth)

    def generate_grid(self) -> npt.NDArray[np.uint8]:
        vfunc = np.vectorize(self.get_cell_state)
        to_return = np.fromfunction(vfunc, self.grid_size)
        return to_return

    def get_cell_state(self, x: int, y: int, z: int) -> np.uint8:
        if random.uniform(0, 1) <= self.alive_chance:
            return BinaryCellState.ALIVE.value
        return BinaryCellState.DEAD.value
