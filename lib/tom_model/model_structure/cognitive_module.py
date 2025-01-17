from lib.tom_model.model_elements.variables import slow_dynamics_variables as slw_dyn, fst_dynamics_variables as fast_dyn


class CognitiveModule:
    def __init__(self, beliefs, goals, emotions=None, biases=None, perceived_knowledge=None,
                 general_world_knowledge=None, general_preferences=None, personality_traits=None, special_beliefs=None):
        """

        Parameters
        ----------
        perceived_knowledge :
        beliefs : List of beliefs of type fast_dyn.Belief
        goals : List of goals of type fast_dyn.Goal
        emotions : List of emotion of type fast_dyn.Emotion
        biases : List of biases of type fast_dyn.Biases
        general_world_knowledge : List of gwk of type slw_dyn.GeneralWorldKnowledge
        general_preferences : ...
        personality_traits : ...
        special_beliefs : List of raw data beliefs of type fast_dyn.BeliefData
        """
        # Fast Dynamics Variables
        self.beliefs, self.goals, self.emotions, self.biases = list(), list(), list(), list()
        self.beliefs_dict, self.goals_dict, self.emotions_dict, self.biases_dict = dict(), dict(), dict(), dict()
        self.add_variables_of_a_type(self.beliefs, self.beliefs_dict, fast_dyn.Belief, beliefs)
        self.add_variables_of_a_type(self.goals, self.goals_dict, fast_dyn.Goal, goals)
        self.add_variables_of_a_type(self.emotions, self.emotions_dict, fast_dyn.Emotion, emotions)
        self.add_variables_of_a_type(self.biases, self.biases_dict, fast_dyn.Bias, biases)
        if perceived_knowledge is not None:
            self.pk, self.pk_dict = list(), dict()
            self.add_variables_of_a_type(self.pk, self.pk_dict, fast_dyn.PerceivedKnowledge, perceived_knowledge)
        else:
            self.pk, self.pk_dict = None, None
        if special_beliefs is not None:
            self.data_beliefs = list()
            self.add_data_belief(special_beliefs)
        else:
            self.data_beliefs = None
        # Slow Dynamics Variables
        self.general_world_knowledge, self.general_preferences, self.personality_traits = list(), list(), list()
        self.general_world_knowledge_dict, self.general_preferences_dict, self.personality_traits_dict = dict(), dict(), dict()
        if general_world_knowledge is not None:
            self.add_variables_of_a_type(self.general_world_knowledge, self.general_world_knowledge_dict,
                                         slw_dyn.GeneralWorldKnowledge, general_world_knowledge)
        if general_preferences is not None:
            self.add_variables_of_a_type(self.general_preferences, self.general_preferences_dict,
                                         slw_dyn.GeneralPreferences, general_preferences)
        if personality_traits is not None:
            self.add_variables_of_a_type(self.personality_traits, self.personality_traits_dict,
                                         slw_dyn.PersonalityTraits, personality_traits)
        for attribute in ['beliefs', 'goals', 'emotions', 'biases', 'general_world_knowledge',
                          'general_preferences', 'personality_traits']:
            setattr(self, attribute, tuple(getattr(self, attribute)))   # make them all tuples instead of lists

    # ************************************* Update Fast Dynamics Variables *************************************
    def compute_and_update_module(self):
        """ First computes the values of all fast-dynamics variables of cognitive module, and then updates them all

        """
        # 1. Compute model_structure core from perceived knowledge
        self.compute_all_variables_next_value()
        # 2. Update value for next time step
        self.update_all_variables_current_value()

    def compute_all_variables_next_value(self):
        """ Computes the values of all fast-dynamics variables that belong to the cognitive module.
        Computes the value of each variable in the next time step according to: x(k+1) = A * x(k) + B * u(k)

        """
        all_variables = self.get_all_fast_dynamics_vars(include_raw_data=True)
        for var in all_variables:  # here, the var.next_value is updated for all variables (using current values)
            if isinstance(var, slw_dyn.SlowDynamicsVariable):
                pass
            elif isinstance(var, fast_dyn.FastDynamicsVariable):
                var.compute_variable_value()

    def update_all_variables_current_value(self):
        """ Updates the values of all the variables that belong to the cognitive module.
        Update the value of each variable in the next time step x(k+1) --> x(k)

        """
        all_variables = self.get_all_fast_dynamics_vars(include_raw_data=False if self.data_beliefs is None else True)
        for var in all_variables:  # here, current value is updated for all variables
            assert isinstance(var, fast_dyn.FastDynamicsVariable)
            var.update_value(learning_rate=0.7)  # we update 0.7 of value (keep 0.3 of previous value)

# ***************************************************** Get Variables **********************************************
    def get_all_fast_dynamics_vars(self, include_raw_data=False):
        """ Returns all the fast dynamics state-variables that were declared in the cognitive module

        Parameters
        ----------
        include_raw_data : if the beliefs that are considered raw data are also returned

        Returns
        -------
        All fast dynamics variables
        """
        if include_raw_data:
            return self.beliefs + self.goals + self.emotions + self.biases + (self.data_beliefs, )
        else:
            return self.beliefs + self.goals + self.emotions + self.biases

    def get_beliefs(self):
        return self.beliefs

    def get_goals(self):
        return self.goals

    def get_emotions(self):
        return self.emotions

    def get_belief_data(self):
        return self.data_beliefs

    def get_biases(self):
        return self.biases

    def get_a_specific_belief(self, name: str):
        return self.beliefs_dict[name]

    def get_a_specific_goal(self, name: str):
        return self.goals_dict[name]

    def get_a_specific_emotion(self, name: str):
        return self.emotions_dict[name]

    def get_a_specific_bias(self, name: str):
        return self.biases_dict[name]

    def get_all_slow_dynamics_vars(self):
        return self.general_world_knowledge + self.general_preferences + self.personality_traits

    def get_all_variables(self, include_raw_data=False):
        return self.get_all_fast_dynamics_vars(include_raw_data) + self.get_all_slow_dynamics_vars()

    # ******************************************* Add Variables  *******************************************

    def add_variables_of_a_type(self, list_2_add, list_dict, variables_type, variables):
        assert isinstance(variables, (list, tuple, dict))
        if isinstance(variables, (list, tuple)):  # iterate through the group of variables if it is a list
            for var in variables:
                self.add_variable(var, variables_type, list_2_add)
        else:
            for var_key in variables:  # iterate through the group of variables if it is a dict
                self.add_variable(variables[var_key], variables_type, list_2_add)
                list_dict[var_key] = variables[var_key]

    def add_variable(self, var, type_of_var, array):
        if isinstance(var, type_of_var):
            array.append(var)
            return
        elif isinstance(var, list):
            for v in var:
                self.add_variable(v, type_of_var, array)
        else:
            TypeError('Variable is not of correct type')

    def add_data_belief(self, var):
        if not isinstance(self.data_beliefs, list):
            self.data_beliefs = [self.data_beliefs]
        self.add_variable(var, fast_dyn.BeliefData, self.data_beliefs)
        if len(self.data_beliefs) == 1:
            self.data_beliefs = self.data_beliefs[0]
