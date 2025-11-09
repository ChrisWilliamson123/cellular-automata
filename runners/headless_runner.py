# A headless runner which iterates an automaton with no speed limit
import time

from typing import Callable, List

from automata.automaton import Automaton

def run(automaton_function: Callable[[], Automaton]):
    automaton = automaton_function()

    start = time.time()
    while True:
        automaton.iterate(0)
        if automaton.iteration_index > 0 and automaton.total_iterations % 10 == 0:
            current = time.time()
            print(automaton.iteration_index, f'{1 / ((current - start) / automaton.total_iterations):.0f} FPS')