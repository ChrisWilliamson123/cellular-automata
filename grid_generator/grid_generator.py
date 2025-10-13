import numpy as np
import numpy.typing as npt
import pygame
from abc import ABC, abstractmethod
from typing import Annotated, Tuple

class GridSizeNotValidError(Exception):
    def __init__(self):
        super().__init__('grid_size must be an odd number')

class GridGenerator(ABC):
    def __init__(self, screen_size: Tuple[int, int], grid_size: Annotated[int, 'must be an odd number'], center: Tuple[int, int]):
        if grid_size % 2 == 0:
            raise GridSizeNotValidError()

        self.screen_size = screen_size
        self.grid_size = grid_size
        self.center = center

    def generate_grid(self) -> npt.NDArray[np.uint8]:
        vfunc = np.vectorize(self.get_cell_state)
        to_return = np.fromfunction(vfunc, (self.grid_size, self.grid_size))
        return to_return
        # state = {}
        # for y in range(int(self.center[1] - (self.grid_size / 2)), int(self.center[1] + (self.grid_size / 2)) + 1):
        #     for x in range(int(self.center[0] - (self.grid_size / 2)), int(self.center[0] + (self.grid_size / 2)) + 1):
        #         if cell_state := self.get_cell_state((x, y)):
        #             state[(x, y)] = cell_state

        # return state

    @abstractmethod
    def get_cell_state(self, x: int, y: int) -> np.uint8:
        pass
