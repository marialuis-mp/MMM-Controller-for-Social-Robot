class Settings:
    def __init__(self, n_iterations: int, initial_learning_rate: float, changing_learning_rate: bool,
                 differentiation_step: float, max_differentiation_step: float, verbose: int = 2,
                 boundary_values: tuple = (0, 1),
                 min_number_of_runs: int = 20, max_number_of_runs: int = 100, default_number_of_runs: int = 100,
                 learning_rate_decay: float = -0.01, multiprocess: bool = True,
                 randomly_initialize_parameters: bool = False, compute_cost_at_end_of_iteration: bool = False,
                 save_each_it_to_excel: bool = False, write_to_excel: bool = True, prune_by_epsilon: bool = False,
                 epsilon=0.01, prune_half_time: bool = False, prune_half_time_error=0.3):
        # data output
        self.verbose = verbose      # 0: nothing / 1: only iteration / 2: + parameter / 3: + each parameter's gradient
        self.save_immediately_to_excel = save_each_it_to_excel
        self.write_to_excel = write_to_excel
        # optimisation characteristics
        self.n_iterations = n_iterations
        self.randomly_initialize_parameters = randomly_initialize_parameters
        self.compute_cost_at_end_of_iteration = compute_cost_at_end_of_iteration
        self.min_value_of_parameters = boundary_values[0]
        self.max_value_of_parameters = boundary_values[1]
        self.boundary_values = boundary_values
        self.multiprocess = multiprocess
        self.min_n_runs = min_number_of_runs
        self.max_n_runs = max_number_of_runs
        self.default_n_runs = default_number_of_runs
        # learning rate
        self.initial_learning_rate = initial_learning_rate
        self.current_learning_rate = initial_learning_rate
        self.varying_learning_rate = changing_learning_rate
        self.learning_rate_decay = learning_rate_decay
        # differentiation step
        self.step = differentiation_step
        self.current_step = differentiation_step
        self.maximum_step = max_differentiation_step
        # prune
        self.prune_by_epsilon = prune_by_epsilon
        self.epsilon = epsilon
        self.prune_half_time = prune_half_time  # prunes at half-time if value is more than 'prune_half_time_error'
        self.prune_half_time_error = prune_half_time_error  # of best value
        self.cost_required_half_time = 0

    def get_range_values(self):
        return self.min_value_of_parameters, self.max_value_of_parameters

    def set_cost_required_half_time(self, current_best_cost):
        self.cost_required_half_time = current_best_cost * (1 + self.prune_half_time_error)
