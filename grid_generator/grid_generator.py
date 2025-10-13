import numpy as np
import numpy.typing as npt
from abc import ABC, abstractmethod
from typing import Tuple

class GridGenerator(ABC):
    def __init__(self, screen_size: Tuple[int, int], grid_size_percentage: int, center: Tuple[int, int]):
        self.screen_size = screen_size
        self.grid_size_percentage = grid_size_percentage
        self.center = center
        width = int(self.screen_size[0] * self.grid_size_percentage)
        if width % 2 == 0:
            width -= 1
        height = int(self.screen_size[1] * self.grid_size_percentage)
        if height % 2 == 0:
            height -= 1
        self.grid_size = (width, height)

    def generate_grid(self) -> npt.NDArray[np.uint8]:
        vfunc = np.vectorize(self.get_cell_state)
        print(self.grid_size)

        to_return = np.fromfunction(vfunc, self.grid_size)
        return to_return

    @abstractmethod
    def get_cell_state(self, x: int, y: int) -> np.uint8:
        pass
