from lib.tom_model.model_structure import cognitive_module, perception_module, decision_making_module


class TomModel:
    def __init__(self, the_cognitive_module: cognitive_module.CognitiveModule,
                 the_decision_making_module: decision_making_module.DecisionMakingModule,
                 the_perception_module: perception_module.PerceptionModule,
                 time_steps4convergence: int):
        """ Declares the Theory of Mind (ToM) model_structure with all its submodules (modules, cognitive, and decision-making
        modules).

        Parameters
        ----------
        the_cognitive_module : the module with the fast- and slow-dynamics state variables
        the_decision_making_module : the module that computes the optimal action based on the fast-dynamics state
            variables
        the_perception_module : the module that computes the beliefs based on the data of the environment
        time_steps4convergence : how much frequency of the internal ToM model_structure is faster than the frequency to
        """
        self.cognitive_module = the_cognitive_module
        self.perception_module = the_perception_module
        self.decision_making_module = the_decision_making_module
        self.time_steps4convergence = time_steps4convergence

    def update_entire_model(self, compute_optimal_action: bool = True):
        """ Updates the entire model_structure core sequentially a certain number of times (time_steps4convergence) and updates
        the values of the variables. Each time, it computes the values of the three modules sequentially, and once ALL
        values are computed, they are updated (at the end of the time). This is repeated 'time_steps4convergence' times.

        Parameters
        ----------
        compute_optimal_action : True if we need to compute the optimal action (done in the output module). If we are
        only interested in estimating mental states, we can set this variable to False.
        """
        # 1. Propagate RLD --> FIS/intention selector for some time steps (faster frequency than action loop)
        for k in range(self.time_steps4convergence):
            # 1. Compute all modules
            self.perception_module.compute_new_value()
            self.cognitive_module.compute_all_variables_next_value()
            if compute_optimal_action:
                self.decision_making_module.compute_new_value(compute_action=False)
            # 2. Update all values
            self.perception_module.update_values_of_module()
            self.cognitive_module.update_all_variables_current_value()
            if compute_optimal_action:
                self.decision_making_module. update_values_of_module(update_action=False)
        # 2. Query for action
        if compute_optimal_action:
            self.decision_making_module.compute_new_value(compute_action=True)
            self.decision_making_module.update_values_of_module(update_action=True)

    def update_entire_model_in_1_go(self, compute_optimal_action):
        """ This function assumes that the three modules run independently at different frequencies. With this
        assumption, it computes each module and updates it right away. Thus, some information computed by repeating the
        model_structure calculations several times is irrelevant, and this function ignores it.
        ++ Pros: It is more efficient
        -- Cons: It does not respect state space formal representation if we consider model_structure as whole system.
                 CAN ONLY be used if modules are independent systems

        Parameters
        ----------
        compute_optimal_action : True if we need to compute the optimal action (done in the output module). If we are
        only interested in estimating mental states, we can set this variable to False.
        """
        # 1. Input module: Needs 2 time steps to converge
        self.perception_module.compute_and_update_module_in_1_go()
        for k in range(self.time_steps4convergence):
            self.cognitive_module.compute_and_update_module()
        if compute_optimal_action:
            self.decision_making_module.compute_and_update_module_in_1_go()

    def get_all_variables(self, get_raw_data=False):
        """ Returns the variables from the model_structure (i.e., variables from cognitive module and from modules module)

        Parameters
        ----------
        get_raw_data : whether the raw data (which is of a different type and class) is returned

        Returns
        -------
        all variables of model_structure core
        """
        return self.cognitive_module.get_all_variables() + self.perception_module.get_overall_output(get_raw_data)
