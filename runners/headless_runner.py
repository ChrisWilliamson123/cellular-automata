# A headless runner which iterates an automaton with no speed limit
import time

from typing import Callable, List

from automata.automaton import Automaton

def run(automaton_function: Callable[[], Automaton]):
    automaton = automaton_function()

    start = time.time()
    while True:
        automaton.iterate(0)
        if automaton.iterations > 0 and automaton.iterations % 1000 == 0:
            current = time.time()
            print(automaton.iterations, f'{1 / ((current - start) / automaton.iterations):.0f} FPS')