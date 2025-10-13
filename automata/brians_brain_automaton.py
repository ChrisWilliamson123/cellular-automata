from enum import Enum
from typing import List, Tuple

import pygame

from automata.automaton import Automaton
from grid_generator.binary_grid_generator import BinaryGridGenerator

class BriansBrainCellState(Enum):
    ALIVE=1
    DEAD=0
    DYING=2

class BriansBrainAutomaton(Automaton):
    def __init__(self, grid_generators: List[BinaryGridGenerator], name: str, screen_size: Tuple[int, int]):
        super().__init__(grid_generators, name)
        self.screen_size = screen_size

    def get_next_state(self, _) -> dict[Tuple[int, int], BriansBrainCellState]:
        alive_neighbour_counts = {}
        dying_neighbour_counts = {}
        alive_cells = set()
        dying_cells = set()
        for ((x, y), state) in self.state.items():
            if state == BriansBrainCellState.ALIVE:
                alive_cells.add((x, y))
                for dx, dy in self.NEIGHBOUR_COORDS:
                    neighbour = ((x + dx) % self.screen_size[0], (y + dy) % self.screen_size[1])
                    alive_neighbour_counts[neighbour] = alive_neighbour_counts.get(neighbour, 0) + 1
            elif state == BriansBrainCellState.DYING:
                dying_cells.add((x, y))
                for dx, dy in self.NEIGHBOUR_COORDS:
                    neighbour = ((x + dx) % self.screen_size[0], (y + dy) % self.screen_size[1])
                    dying_neighbour_counts[neighbour] = dying_neighbour_counts.get(neighbour, 0) + 1

        new_state = {}

        # 1. A cell turns on if it was off but had exactly two neighbors that were on.
        for (coord, count) in alive_neighbour_counts.items():
            cell_off = coord not in alive_cells and coord not in dying_cells
            if cell_off and count == 2:
                new_state[coord] = BriansBrainCellState.ALIVE

        # 2. All cells that were "on" go into the "dying" state, which is not counted as an "on" cell in the neighbor count. and prevents any cell from being born there.
        for coord in alive_cells:
            new_state[coord] = BriansBrainCellState.DYING

        # 3. Cells that were in the dying state go into the off state.
        # Don't need to do anything for 3. as the dying cells are not already in new_state
        return new_state

    def render(self, surface):
        for (coord, state) in self.state.items():
            pygame.draw.rect(surface, (255, 255, 255) if state == BriansBrainCellState.ALIVE else (124, 157, 163), pygame.Rect(coord, (1, 1)))

    def debug_string(self):
        # return f'{self.bs_notation}, GS: {initial_size}, AC: {alive_chance:.2f}'
        return ''
