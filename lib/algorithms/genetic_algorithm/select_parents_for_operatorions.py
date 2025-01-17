import random
import time
from enum import Enum
from copy import copy, deepcopy

from lib.algorithms.genetic_algorithm.Solution import Solution


class ParentSelection(Enum):
    TOURNAMENT = 1
    FITNESS = 2


def select_parents(ranked_solutions, mode: ParentSelection, n_to_select, settings):
    st = time.time()
    if mode == ParentSelection.TOURNAMENT:
        parent_solutions = select_parents_tournament(ranked_solutions, n_to_select, settings.n_solutions_in_tournament)
    elif mode == ParentSelection.FITNESS:
        parent_solutions = select_parents_fitness(ranked_solutions, n_to_select, settings.max_value_fitness)
    if settings.verbose > 2:
        print('     time to select parents: ', time.time() - st)
    return parent_solutions


def select_parents_tournament(ranked_solutions: list[Solution], n_to_select, n_solutions_in_tournament):
    assert n_to_select < len(ranked_solutions)
    parent_solutions = []
    solutions_indices = list(range(len(ranked_solutions)))
    for i in range(n_to_select):
        candidates = random.sample(solutions_indices, n_solutions_in_tournament)
        tournament_winner_index = min(candidates)
        solutions_indices.remove(tournament_winner_index)
        parent_solutions.append(deepcopy(ranked_solutions[tournament_winner_index]))
    return parent_solutions


def select_parents_fitness(ranked_solutions: list[Solution], n_to_select, max_value_fitness=10e10):
    assert n_to_select < len(ranked_solutions)
    parent_solutions = []
    copy_solutions = ranked_solutions.copy()
    i = 0
    while i < n_to_select:
        candidate = random.choice(copy_solutions)
        if candidate.fitness > random.uniform(0, max_value_fitness):
            parent_solutions.append(deepcopy(candidate))
            copy_solutions.remove(candidate)
            i += 1
    return parent_solutions
