import random


def arithmetic_crossover(parent_solutions, alpha=0.5):
    children_solutions = []
    while len(parent_solutions) > 1:
        p1 = parent_solutions.pop(0)
        p2 = parent_solutions.pop(0)
        k = random.randint(0, len(p1.parameters) - 1)
        c1_par_k = alpha * p1.parameters[k] + (1 - alpha) * p2.parameters[k]
        c2_par_k = alpha * p2.parameters[k] + (1 - alpha) * p1.parameters[k]
        p1.parameters[k] = c1_par_k
        p2.parameters[k] = c2_par_k
        children_solutions.extend((p1, p2))
    return children_solutions


def mutation(parent_solutions, mutation_range, parameters):
    for solution in parent_solutions:
        k = random.randint(0, len(solution.parameters) - 1)
        solution.parameters[k] += random.uniform(-mutation_range, mutation_range)
        solution.parameters[k] = max(min(solution.parameters[k], parameters[k].maximum_value), parameters[k].minimum_value)
    return parent_solutions
