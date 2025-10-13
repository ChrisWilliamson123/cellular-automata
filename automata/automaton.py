from abc import ABC, abstractmethod
import numpy as np
import numpy.typing as npt
from typing import List, Tuple, TypeVar

from grid_generator.grid_generator import GridGenerator

State = TypeVar('State', bound=np.generic, covariant=True)

class Automaton(ABC):
    state: npt.NDArray[np.uint8]

    def __init__(self, grid_generators: List[GridGenerator], name: str):
        self.grid_generators = grid_generators
        self.name = name
        self.paused = False
        self.reset()

    def iterate(self, dt):
        if self.paused:
            return
        new_state = self.get_next_state(dt)

        self.prev_states[0] = self.prev_states[1]
        self.prev_states[1] = self.state
        self.state = new_state

        if self.should_reset():
            self.reset()

    @abstractmethod
    def get_next_state(self) -> npt.NDArray[np.uint8]:
        pass

    @abstractmethod
    def render(self, surface):
        pass

    def should_reset(self) -> bool:
        return (self.state == self.prev_states[0]).all()
    
    @abstractmethod
    def debug_string(self) -> str:
        pass

    def reset(self):
        master_grid = np.zeros(self.grid_generators[0].screen_size, dtype=np.int8)
        for g in self.grid_generators:
            grid = g.generate_grid()
            l = g.center[0] - (g.grid_size[0] // 2)
            t = g.center[1] - (g.grid_size[1] // 2)
            master_grid[l:l+g.grid_size[0], t:t+g.grid_size[1]] = grid
        self.state = master_grid
        self.prev_states = [None, None]

    def cleanup(self):
        pass

    def toggle_pause(self):
        self.paused = not self.paused