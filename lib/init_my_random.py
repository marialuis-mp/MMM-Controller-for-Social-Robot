import random
import sys


def init_random(seed):
    if seed is None:
        seed = random.randrange(sys.maxsize)
    random_ = random.Random(seed)
    return random_
