import random

def get_random_odd_number(start, end):
    while True:
        random_number = random.randint(start, end)
        if random_number % 2 != 0:
            return random_number
