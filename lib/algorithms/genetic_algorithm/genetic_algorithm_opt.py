import random
import time

from lib.algorithms.genetic_algorithm.Solution import Solution
from lib.algorithms.genetic_algorithm import operators
from lib.algorithms.genetic_algorithm.select_parents_for_operatorions import select_parents


def run_ga(parameters, settings, cost_function):
    solutions = generate_solutions(settings.n_solutions, parameters)
    evaluate_solutions(solutions, parameters, cost_function, settings)
    for i in range(settings.n_iterations):
        st = time.time()
        ranked_solutions = rank_solutions(solutions)
        elite_sols, crossover_sols, mutation_sols = apply_evolution_operations(ranked_solutions.copy(), parameters, settings)
        solutions = elite_sols + evaluate_solutions(crossover_sols + mutation_sols, parameters, cost_function, settings)
        output_info(settings, i, ranked_solutions, st)
    return ranked_solutions


def output_info(settings, it, ranked_solutions, starting_time):
    if settings.verbose > 0:
        # print('Gen ', it, ' best solutions: ', [s.fitness for s in ranked_solutions[0:1]], )
        print('Gen ', it, ' best solution: ', ranked_solutions[0].fitness, ' parameters: ', ranked_solutions[0].parameters)
        if settings.verbose > 1:
            print('     time of iteration: ', time.time() - starting_time)


def fitness_function(parameters, cost_function, settings):
    cost = cost_function(parameters)
    if cost == 0:
        return settings.max_value_fitness
    else:
        return 1/cost


def generate_solutions(number_of_solutions, parameters):
    solutions = []
    for s in range(number_of_solutions):
        solution_params = []
        for par in parameters:
            solution_params.append(random.uniform(par.minimum_value, par.maximum_value))
        solutions.append(Solution(0, solution_params))
    return solutions


def evaluate_solutions(solutions, parameters, cost_function, settings):
    for s in solutions:
        for i in range(len(parameters)):
            parameters[i].value = s.parameters[i]
        s.fitness = fitness_function(parameters, cost_function, settings)
    return solutions


def rank_solutions(evaluated_solutions):
    evaluated_solutions.sort(reverse=True, key=lambda solution: solution.fitness)
    return evaluated_solutions


def apply_evolution_operations(ranked_solutions, parameters, settings):
    elite_solutions = ranked_solutions[0:settings.n_elite]
    parent_solutions = select_parents(ranked_solutions, settings.parent_selection_method, settings.n_crossover, settings)
    crossover_solutions = operators.arithmetic_crossover(parent_solutions, alpha=settings.arithmetic_crossover_weight)
    parent_solutions = select_parents(ranked_solutions, settings.parent_selection_method, settings.n_mutation, settings)
    mutation_solutions = operators.mutation(parent_solutions, settings.mutation_range, parameters)
    return elite_solutions, crossover_solutions, mutation_solutions
