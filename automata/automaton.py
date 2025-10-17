from abc import ABC, abstractmethod
import numpy as np
import numpy.typing as npt
from typing import List, Tuple, TypeVar

import pygame

from grid_generator.grid_generator import GridGenerator

State = TypeVar('State', bound=np.generic, covariant=True)

class AutomatonRewindError(Exception):
    pass

class Automaton(ABC):
    state: npt.NDArray[np.uint8]

    def __init__(self, grid_generators: List[GridGenerator], name: str):
        self.grid_generators = grid_generators
        self.name = name
        self.iteration_index = 0
        self.total_iterations = 0
        self.iterations = []
        self.colours = self.default_colours
        self.reset()

    def iterate(self, dt):
        if self.iteration_index < self.total_iterations - 1:
            self.state = self.iterations[self.iteration_index + 1]
            self.iteration_index += 1
            return

        new_state = self.get_next_state(dt)

        self.prev_states[0] = self.prev_states[1]
        self.prev_states[1] = self.state
        self.state = new_state
        self.iterations.append(self.state)
        self.total_iterations += 1
        self.iteration_index += 1

        if self.should_reset():
            self.reset()

    def rewind(self):
        if self.total_iterations > 0:
            if self.iteration_index > 0:
                self.state = self.iterations[self.iteration_index - 1]
                self.iteration_index -= 1
            else:
                raise AutomatonRewindError('At start of iterations')
        else:
            raise AutomatonRewindError('No iterations available')

    @abstractmethod
    def get_next_state(self) -> npt.NDArray[np.uint8]:
        pass

    @abstractmethod
    def render(self, surface: pygame.Surface):
        pass

    @abstractmethod
    def get_frame(self) -> npt.NDArray[np.uint8]:
        pass

    def should_reset(self) -> bool:
        return (self.state == self.prev_states[0]).all()
    
    @abstractmethod
    def debug_string(self) -> str:
        pass

    def subtitle(self) -> str:
        ''

    def reset(self):
        master_grid = np.zeros(self.grid_generators[0].screen_size, dtype=np.int8)
        for g in self.grid_generators:
            grid = g.generate_grid()
            l = g.center[0] - (g.grid_size[0] // 2)
            t = g.center[1] - (g.grid_size[1] // 2)
            master_grid[l:l+g.grid_size[0], t:t+g.grid_size[1]] = grid
        self.state = master_grid
        self.prev_states = [None, None]
        self.iteration_index = 0
        self.total_iterations = 1
        self.iterations = [self.state]

    def cleanup(self):
        pass

    @property
    @abstractmethod
    def default_colours(self) -> npt.NDArray[np.uint8]:
        pass

    def change_colours(self, colours):
        self.colours = np.array(colours, dtype=np.uint8)