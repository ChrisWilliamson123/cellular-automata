from enum import Enum
from typing import List, Tuple

import numpy as np
import numpy.typing as npt
import pygame

from automata.automaton import Automaton
from grid_generator.binary_grid_generator import BinaryGridGenerator

class BriansBrainCellState(Enum):
    ALIVE=1
    DEAD=0
    DYING=2

class BriansBrainAutomaton(Automaton):
    COLOURS = np.array([
        (0, 0, 0),       # DEAD
        (255, 255, 255), # ALIVE
        (124, 157, 163)  # DYING
    ], dtype=np.uint8)

    def __init__(self, grid_generators: List[BinaryGridGenerator], name: str, screen_size: Tuple[int, int]):
        super().__init__(grid_generators, name)
        self.screen_size = screen_size
    
    def get_next_state(self, _) -> npt.NDArray[np.int8]:
        # Mask for alive cells
        alive = (self.state == 1)

        # Count alive neighbors (8-connected)
        alive_neighbors = sum(
            np.roll(np.roll(alive, dy, axis=0), dx, axis=1)
            for dy in (-1, 0, 1)
            for dx in (-1, 0, 1)
            if not (dx == 0 and dy == 0)
        )

        # Prepare next state array
        new_state = np.zeros_like(self.state)

        # Rule 1: alive → dying
        new_state[self.state == 1] = 2

        # Rule 2: dying → dead (already 0 in new_state)

        # Rule 3: dead → alive if exactly 2 alive neighbors
        new_state[(self.state == 0) & (alive_neighbors == 2)] = 1

        return new_state

    def render(self, surface):
        coloured = BriansBrainAutomaton.COLOURS[self.state]
        grid_surface = pygame.surfarray.make_surface(coloured)
        surface.blit(grid_surface, (0, 0))

    def debug_string(self):
        # return f'{self.bs_notation}, GS: {initial_size}, AC: {alive_chance:.2f}'
        return ''
