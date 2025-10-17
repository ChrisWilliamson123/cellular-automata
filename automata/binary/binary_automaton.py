import numpy as np
import numpy.typing as npt
from typing import List, Tuple
import pygame

from automata.automaton import Automaton
from grid_generator.binary_grid_generator import BinaryCellState, BinaryGridGenerator
from grid_generator.grid_generator import GridGenerator
from helpers import random_bs_notation

class BinaryAutomaton(Automaton):
    def __init__(self, grid_generators: List[BinaryGridGenerator], name: str, bs_notation: str, screen_size: Tuple[int, int]):
        self.bs_notation = bs_notation
        self.birth_rules, self.survival_rules = self._parse_bs_rule(bs_notation)
        self.birth_rules = np.array(self.birth_rules)
        self.survival_rules = np.array(self.survival_rules)
        self.screen_size = screen_size
        super().__init__(grid_generators, name)

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
        # self.state: 2D array of ints (e.g., 0..N-1)
        # self.colours: list or array of shape (N, 4) or (N, 3) with RGB or RGBA values

        # Ensure colours is a NumPy array for indexing
        colours = np.array(self.colours, dtype=np.uint8)

        # Use advanced indexing to map each cell value to its RGBA colour
        rgba = colours[self.state]

        # If your colours only contain RGB values, add an alpha channel
        if rgba.shape[-1] == 3:
            alpha = np.full((*self.state.shape, 1), 255, dtype=np.uint8)
            rgba = np.concatenate([rgba, alpha], axis=-1)

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
    
    @property
    def default_colours(self) -> npt.NDArray[np.uint8]:
        return np.array([
            (0, 0, 0),       # Dead
            (255, 255, 255)  # Alive
        ], dtype=np.uint8)

class RandomBinaryAutomaton(BinaryAutomaton):
    def __init__(self, grid_generators: List[BinaryGridGenerator], name: str, screen_size: Tuple[int, int]):
        bs_notation = random_bs_notation()
        super().__init__(grid_generators, name, bs_notation, screen_size)

    def randomise_notation(self):
        self.bs_notation = random_bs_notation()
        self._set_rules()
        self.reset()

    def submit_notation(self, notation):
        self.bs_notation = notation
        self._set_rules()
        self.reset()

    def _set_rules(self):
        self.birth_rules, self.survival_rules = self._parse_bs_rule(self.bs_notation)
        self.birth_rules = np.array(self.birth_rules)
        self.survival_rules = np.array(self.survival_rules)
