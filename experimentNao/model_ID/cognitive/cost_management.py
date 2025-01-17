class Cost:
    def __init__(self, state_vars, vars_2_id, vars_w_linkages_to_id, tom_model, n_horizon, simplified_dynamics):
        """ object that manages the cost function and the performance of the identification process

        Parameters
        ----------
        state_vars : Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion]
        vars_2_id : List[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]
        vars_w_linkages_to_id : Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion]
        tom_model : experimentNao.declare_model.declare_entire_model.ToMModelChessSimpleDyn
        n_horizon : int
        simplified_dynamics : bool
        """
        self.state_vars = state_vars
        self.vars_2_id = vars_2_id
        self.vars_w_linkages_to_id = vars_w_linkages_to_id
        self.tom_model = tom_model
        self.n_horizon = n_horizon
        self.simplified_dynamics = simplified_dynamics

    def cost_function(self, parameters_2_id, training_steps, parameters_manager, vars_2_id=None):
        """ definition of the cost function used in the identification process

        Parameters
        ----------
        parameters_2_id : List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]
        training_steps : List[int]
        parameters_manager : experimentNao.model_ID.cognitive.parameters_manager.ParametersManager
        vars_2_id : Union[None]

        Returns
        -------
        numpy.float64
        """
        vars_2_id = self.vars_2_id if vars_2_id is None else vars_2_id
        if self.simplified_dynamics:  # time step equivalent to the training step
            return self.cost_function_simple_dynamics(parameters_2_id, training_steps, parameters_manager, vars_2_id)
        else:
            return self.cost_function_cmp_dynamics(parameters_2_id, training_steps, parameters_manager, vars_2_id)

    def cost_function_cmp_dynamics(self, parameters_2_id, training_steps, parameters_manager, vars_2_id):
        """ cost function used when complex dynamics are active - not used in the experiment

        Parameters
        ----------
        parameters_2_id : List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]
        training_steps : List[int]
        parameters_manager : experimentNao.model_ID.cognitive.parameters_manager.ParametersManager
        vars_2_id : Union[None]


        Returns
        -------

        """
        parameters_manager.set_values_of_parameters(parameters_2_id, self.vars_w_linkages_to_id)
        cost = 0
        for this_train_step in training_steps:
            k = self.n_horizon * this_train_step + 1    # time step equivalent to the training step
            k0 = k - self.n_horizon  # time step of starting data point -> k_0 = k - n_horizon
            self.set_values_of_vars_in_time_step_k(k0)  # *** 1. Set values for time step k_0
            for j in range(self.n_horizon):  # *** 2. Run module n_horizon times
                self.tom_model.perception_module.perceptual_access.inputs.set_current_input_from_sequence(k0 + j + 1)
                self.tom_model.update_entire_model_in_1_go(compute_optimal_action=False)
            for var in vars_2_id:  # Compute cost of prediction in time step = step
                cost += (var.values[k] - var.value) ** 2
        return cost

    def cost_function_simple_dynamics(self, parameters_2_id, training_steps, parameters_manager, vars_2_id):
        """ cost function used when complex dynamics are not active

        Parameters
        ----------
        parameters_2_id : List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]
        training_steps : List[int]
        parameters_manager : experimentNao.model_ID.cognitive.parameters_manager.ParametersManager
        vars_2_id : List[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]

        Returns
        -------
        numpy.float64
        """
        weights = [0.75, 0.25] if self.n_horizon == 2 else [1] if self.n_horizon == 1 else None
        parameters_manager.set_values_of_parameters(parameters_2_id, self.vars_w_linkages_to_id)
        cost = 0
        for k in training_steps:
            try:
                k0 = k - 1  # time step of starting data point -> k_0 = k - 1
                self.set_values_of_vars_in_time_step_k(k0)  # *** 1. Set values for time step k_0
                for j in range(self.n_horizon):  # *** 2. Run module n_horizon times
                    k_j = k + j
                    self.tom_model.perception_module.perceptual_access.inputs.set_current_input_from_sequence(k_j)
                    self.tom_model.update_entire_model_in_1_go(compute_optimal_action=False)
                    for var in vars_2_id:  # Compute cost of prediction in time step = step
                        cost += weights[j] * ((var.values[k_j] - var.value) ** 2)
            except IndexError:
                print('Index error')
        return cost

    def set_values_of_vars_in_time_step_k(self, k):
        """ sets the values of the variable for a time step k, according to the training data

        Parameters
        ----------
        k : int
        """
        for var in self.state_vars:     # here we need to set values of ALL state vars, not just vars 2 ID, because some
            var.value = var.values[k]      # the vars 2 ID at k0+1 will depend on ALL state vars at k0
        self.tom_model.cognitive_module.compute_and_update_biases()  # all biases are computed and updated without dynamic
