from collections import defaultdict
import random
from typing import Annotated, List, Tuple

import pygame

from automata.automaton import Automaton
from grid_generator.binary_grid_generator import BinaryCellState
from grid_generator.grid_generator import GridGenerator

class CyclicGridGenerator(GridGenerator):
    def __init__(self, grid_size: Annotated[int, 'must be an odd number'], center: Tuple[int, int], alive_chance: Annotated[float, 'in range 0...1'], number_of_states: int):
        super().__init__(grid_size, center)

        self.alive_chance = alive_chance
        self.grid_size = grid_size
        self.number_of_states = number_of_states

    def get_cell_state(self, x: int, y: int) -> int:
        if random.uniform(0, 1) <= self.alive_chance:
            return random.randint(0, self.number_of_states - 1)

class CyclicAutomaton(Automaton):
    PALETTE = [
        (255, 173, 173), (255, 214, 165), (253, 255, 182), (202, 255, 191),
        (155, 246, 255), (160, 196, 255), (189, 178, 255), (255, 198, 255),
        (255, 255, 252), (228, 240, 240)
    ]
    def __init__(self, grid_generators: List[CyclicGridGenerator], name: str, screen_size: Tuple[int, int], number_of_states: int):
        super().__init__(grid_generators, name)

        self.number_of_states = number_of_states
        self.screen_size = screen_size

    def get_next_state(self, _) -> dict[Tuple[int, int], BinaryCellState]:
        neighbours = defaultdict(lambda: defaultdict(int))
        for ((x, y), state) in self.state.items():
            for dx, dy in self.NEIGHBOUR_COORDS:
                neighbour = ((x + dx) % self.screen_size[0], (y + dy) % self.screen_size[1])
                neighbours[neighbour][state] += 1
                # alive_neighbour_counts[neighbour] = alive_neighbour_counts.get(neighbour, 0) + 1

        new_state = {}
        for (coord, neighbour_counts) in neighbours.items():
            values = list(neighbour_counts.values())
            sum_values = sum(values)
            if sum_values < 8:
                neighbour_counts[0] += (8 -sum_values)

            coord_state = self.state[coord] if coord in self.state else 0
            next = (coord_state + 1) % self.number_of_states
            if neighbour_counts[next] > 0:
                new_state[coord] = next

        return new_state

    def render(self, surface):
        for (coord, state) in self.state.items():
            colour = CyclicAutomaton.PALETTE[state]
            pygame.draw.rect(surface, colour, pygame.Rect(coord, (1, 1)))

    def debug_string(self):
        # return f'{self.bs_notation}, GS: {initial_size}, AC: {alive_chance:.2f}'
        return ''
