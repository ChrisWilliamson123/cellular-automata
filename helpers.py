import random

def get_random_odd_number(start, end):
    while True:
        random_number = random.randint(start, end)
        if random_number % 2 != 0:
            return random_number

def random_bs_notation() -> str:
    """
    Generate a random binary cellular automaton rule in B/S notation.
    Example: 'B3/S23' (Conway's Game of Life)
    """
    # Pick random subsets of [0..8] for birth and survival
    birth = sorted(random.sample(range(1, 9), random.randint(1, 8)))
    survival = sorted(random.sample(range(0, 9), random.randint(0, 9)))

    # Convert to string form
    b_str = ''.join(map(str, birth))
    s_str = ''.join(map(str, survival))

    return f"B{b_str}/S{s_str}"