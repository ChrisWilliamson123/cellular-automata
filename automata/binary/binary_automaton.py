import numpy as np
import numpy.typing as npt
from typing import List, Tuple
import pygame

from automata.automaton import Automaton
from grid_generator.binary_grid_generator import BinaryCellState, BinaryGridGenerator
from grid_generator.grid_generator import GridGenerator

class BinaryAutomaton(Automaton):
    COLOURS = np.array([
        (0, 0, 0),       # Dead
        (255, 255, 255)  # Alive
    ], dtype=np.uint8)

    def __init__(self, grid_generators: List[BinaryGridGenerator], name: str, bs_notation: str, screen_size: Tuple[int, int]):
        super().__init__(grid_generators, name)
        self.bs_notation = bs_notation
        self.birth_rules, self.survival_rules = self._parse_bs_rule(bs_notation)
        self.birth_rules = np.array(self.birth_rules)
        self.survival_rules = np.array(self.survival_rules)
        self.screen_size = screen_size

    def get_next_state(self, _) -> npt.NDArray[np.int8]:
        neighbour_counts = sum(
            np.roll(np.roll(self.state, dy, axis=0), dx, axis=1) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dx, dy) != (0, 0)
        )

        new_state = np.where((self.state == BinaryCellState.ALIVE.value) & np.isin(neighbour_counts, self.survival_rules), BinaryCellState.ALIVE.value, BinaryCellState.DEAD.value)
        new_state = np.where((self.state == BinaryCellState.DEAD.value) & np.isin(neighbour_counts, self.birth_rules), BinaryCellState.ALIVE.value, new_state)

        return new_state
    
    def render(self, surface):
        coloured = BinaryAutomaton.COLOURS[self.state]
        grid_surface = pygame.surfarray.make_surface(coloured)
        surface.blit(grid_surface, (0, 0))

    def get_frame(self):
        # Create an RGBA image with white for alive cells and black for dead cells
        rgba = np.zeros((self.state.shape[0], self.state.shape[1], 4), dtype=np.uint8)
        rgba[..., 0] = self.state * BinaryAutomaton.COLOURS[1][0] # Red
        rgba[..., 1] = self.state * BinaryAutomaton.COLOURS[1][1] # Green
        rgba[..., 2] = self.state * BinaryAutomaton.COLOURS[1][2] # Blue
        rgba[..., 3] = 255                                        # Alpha channel always maxed
        return rgba

    def debug_string(self):
        # return f'{self.bs_notation}, GS: {initial_size}, AC: {alive_chance:.2f}'
        return f'{self.bs_notation}'
    
    def subtitle(self):
        return f'B/S Notation: {self.bs_notation}'

    def _parse_bs_rule(self, rule_str):
        """
        Parses a B/S notation string into birth and survival lists.
        
        Parameters:
            rule_str (str): A rule string like 'B3/S23'
            
        Returns:
            tuple: (birth_list, survival_list), both are lists of integers
        """
        if not rule_str.upper().startswith('B') or '/S' not in rule_str.upper():
            raise ValueError("Invalid B/S rule format. Expected format like 'B3/S23'.")

        # Normalize and split
        rule_str = rule_str.upper()
        b_part, s_part = rule_str.split('/')

        birth = [int(n) for n in b_part[1:] if n.isdigit()]
        survival = [int(n) for n in s_part[1:] if n.isdigit()]

        return birth, survival
