from lib.algorithms.genetic_algorithm.select_parents_for_operatorions import ParentSelection


class Settings:
    def __init__(self, n_iterations: int, n_solutions: int, percentage_crossover: float, percentage_mutation: float,
                 parent_selection_method: ParentSelection, n_solutions_in_tournament: int = 4,
                 max_value_fitness: float = 10e10, arithmetic_crossover_weight: float = 0.5, mutation_range: float = 0.1,
                 verbose=1):
        # quantities
        self.n_iterations = n_iterations
        self.n_solutions = n_solutions
        # percentages of parts that are evolved in different ways
        self.percentage_elite = 1 - (percentage_crossover + percentage_mutation)
        self.percentage_crossover = percentage_crossover
        self.percentage_mutation = percentage_mutation
        self.n_crossover = round(percentage_crossover * n_solutions)
        self.n_mutation = round(percentage_mutation * n_solutions)
        self.n_elite = n_solutions - (self.n_crossover + self.n_mutation)
        # selecting parents for evolution settings
        self.parent_selection_method = parent_selection_method
        self.n_solutions_in_tournament = n_solutions_in_tournament
        self.max_value_fitness = max_value_fitness
        # crossover settings
        self.arithmetic_crossover_weight = arithmetic_crossover_weight
        # mutation settings
        self.mutation_range = mutation_range
        self.verbose = verbose
