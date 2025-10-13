from collections import defaultdict
from enum import Enum
import random
from typing import Annotated, List, Tuple
import numpy as np
import numpy.typing as npt

import pygame

from automata.automaton import Automaton
from grid_generator.grid_generator import GridGenerator

class ForestFireState(Enum):
    TREE=1
    BURNING=2
    WATER=3
    DEAD=0

class ForestFireGridGenerator(GridGenerator):
    def __init__(self, screen_size: Tuple[int, int], grid_size_percentage: int, center: Tuple[int, int], tree_chance: Annotated[float, 'in range 0...1'], burning_chance: Annotated[float, 'in range 0...1'], lake_chance: Annotated[float, 'in range 0...1'] = 0, lake_size: int = 0, lake_amount: int = 1):
        super().__init__(screen_size, grid_size_percentage, center)

        self.tree_chance = tree_chance
        self.burning_chance = burning_chance
        self.grid_size_percentage = grid_size_percentage
        self.lake_chance = lake_chance
        self.lake_size = lake_size
        self.lake_amount = lake_amount
    
    def generate_grid(self) -> npt.NDArray[np.uint8]:
        state = super().generate_grid()
        if random.uniform(0, 1) <= self.lake_chance:
            for _ in range(self.lake_amount):
                # lake_x, lake_y = random.randint(int(self.center[0] - (self.grid_size / 2)), int(self.center[0] + (self.grid_size / 2))), random.randint(int(self.center[1] - (self.grid_size / 2)), int(self.center[1] + (self.grid_size / 2)))
                lake_x, lake_y = random.randint(0, self.grid_size[0]), random.randint(0, self.grid_size[1])
                for _ in range(self.lake_size):
                    if lake_y < self.grid_size[1] and lake_x < self.grid_size[0]:
                        state[(lake_x, lake_y)] = ForestFireState.WATER.value
                    lake_x += random.randint(-1, 1)
                    lake_y += random.randint(-1, 1)
        return state

    def get_cell_state(self, x: int, y: int) -> np.uint8:
        if random.uniform(0, 1) <= self.tree_chance:
            if random.uniform(0, 1) <= self.burning_chance:
                return ForestFireState.BURNING.value
            else:
                return ForestFireState.TREE.value
        else:
            return ForestFireState.DEAD.value

class ForestFireAutomaton(Automaton):
    COLOURS = np.array([
        (0, 0, 0),       # Dead
        (21, 92, 15), # TREE
        (255, 119, 41), # BURNING
        (0, 0, 255) # WATER
    ], dtype=np.uint8)

    def __init__(self, grid_generators: List[ForestFireGridGenerator], name: str, screen_size: Tuple[int, int]):
        super().__init__(grid_generators, name)
        self.screen_size = screen_size
        self.sample_rate = 44100
        self.volume = 0.3

        # Fire state (global or injected dynamically)
        self.fire_state = {"trees_remaining": 1.0}  # 1.0 = 100%, 0.0 = all burned

        self.max_trees = None

    def cleanup(self):
        pass

    def get_next_state(self, dt) -> npt.NDArray[np.int8]:
        # Create masks
        burning_mask = (self.state == ForestFireState.BURNING.value)
        tree_mask = (self.state == ForestFireState.TREE.value)

        # Count burning neighbors using np.roll
        burning_neighbors = sum(
            np.roll(np.roll(burning_mask, dy, axis=0), dx, axis=1)
            for dy in (-1, 0, 1)
            for dx in (-1, 0, 1)
            if (dx, dy) != (0, 0)
        )

        # Start with a copy
        new_state = self.state.copy()

        # Rule 1: Burning → Dead
        new_state[burning_mask] = ForestFireState.DEAD.value 
        # Rule 2: Tree → Burning if ANY burning neighbor
        new_state[np.logical_and(tree_mask, burning_neighbors > 0)] = ForestFireState.BURNING.value

        # Rule 3: Water, Dead stay unchanged automatically
        return new_state

    def render(self, surface):
        coloured = ForestFireAutomaton.COLOURS[self.state]
        grid_surface = pygame.surfarray.make_surface(coloured)
        surface.blit(grid_surface, (0, 0))

    def debug_string(self):
        # return f'{self.bs_notation}, GS: {initial_size}, AC: {alive_chance:.2f}'
        return ''
