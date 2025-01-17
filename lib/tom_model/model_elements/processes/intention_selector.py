from abc import ABCMeta

from lib.tom_model.model_elements.variables import fst_dynamics_variables as fst_dyn, \
    decision_making_variables as dm_vars
from lib.tom_model.model_elements.processes import process


class IntentionSelector(process.DecisionMakingProcess):
    __metaclass__ = ABCMeta

    def __init__(self, inputs, outputs, function, input_type, output_type, output_type_parent_class=None):
        """ This is the general implementation of a IntentionSelector class, the 1st process of decision-making module.
        A specific version of the IntentionSelector (dependent on the application) must be implemented by deriving
        this class.

        Parameters
        ----------
        inputs : tuple[tuple]
            Inputs of the process
        outputs : tuple[lib.tom_model.model_elements.variables.dm_variables.Intention]
            Output of the process
        function : function
            The function that is used to process the input(s) and create the output(s)
        input_type : tuple[type]
            Class of inputs allowed for the child class that specifies the process. For example, the input_type
            that is defined for the child class of Intention Selector (e.g., IntentionSelectorHuman) could be
            BeliefOfHuman, since the IntentionSelector receives as input objects of any child class of Belief or Goal.
        output_type : type
            Class of outputs allowed for the child class that specifies the process
        output_type_parent_class : type
            General (parent) classes allowed as outputs of the type of process
        """
        output_type_parent_class = dm_vars.Intention if output_type_parent_class is None else output_type_parent_class
        super().__init__(inputs, outputs, function, input_type=input_type, output_type=output_type,
                         input_type_parent_class=(fst_dyn.Belief, fst_dyn.Goal, fst_dyn.BeliefData),
                         output_type_parent_class=output_type_parent_class)

    def set_function(self, function):
        """ Sets the function that represents the process and checks whether it is allowed or not.

        Parameters
        ----------
        function : function
            Method that represents the specified IntentionSelector process. This function must be a method of a
            child class of the IntentionSelector class (the specifically implemented IntentionSelector child class that
            depends on the application).
        """
        if IntentionSelector.__qualname__ in function.__qualname__:
            self.function = function
        else:
            raise TypeError('process function is not a method of this process class')


class IntentionSelectorThreshold(IntentionSelector):
    def __init__(self, inputs, outputs, function, input_type=None, output_type=None):
        """ Child class of Intention Selector, where the intentions are considered to be triggered (active) if they
        surpass a certain threshold value.

        Parameters
        ----------
        inputs :
        outputs :
        function :
        input_type :
        output_type :
        """
        input_type = (fst_dyn.Belief, fst_dyn.BeliefData, fst_dyn.Goal) if input_type is None else input_type
        output_type = dm_vars.IntentionThreshold if output_type is None else output_type
        super().__init__(inputs, outputs, function, input_type, output_type,
                         output_type_parent_class=dm_vars.IntentionThreshold)
        self.active_intentions = []
        self.check_if_influencers_of_intentions_are_inputs()  # make sure all the influencers of the outputs are inputs

    def activate_intentions_by_threshold_fast(self):
        """ predicts the active intentions of the human given the thresholds that are set for each intention. If for an
        intention, a threshold is defined, then the intention is only activated if the corresponding goal has a value
        larger than the threshold. In this function, the corresponding goal is the one saved in intention object.
        In this function, it is not checked whether this goal is a valid input. Thus, if this function is used for  the
        selector, the function 'self.check_if_influencers_of_intentions_are_inputs' should be run in the constructor,
        once all the intentions have been declared.

        """
        self.deactivate_all_intentions()
        for intention in self.outputs:
            self.activate_1_intention_by_threshold_fast(intention)

    def activate_1_intention_by_threshold_fast(self, intention):
        """ activates one intention if the value of its goal is higher than the threshold. Does this in a fast way, as
        described in the documentation of 'activate_intentions_by_threshold_fast'

        Parameters
        ----------
        intention : lib.tom_model.model_elements.variables.dm_variables.IntentionThreshold
            the intention that will be checked
        """
        if intention.belief is None:
            if is_value_over_threshold(intention.goal.value, intention.threshold, intention.larger_than_threshold):
                self.activate_intention(intention)
        else:
            if is_value_over_threshold(intention.goal.value,
                                       (intention.threshold + intention.belief.value * intention.belief_contribution),
                                       intention.larger_than_threshold):
                self.activate_intention(intention)

    def activate_intentions_by_threshold(self):  # todo compute speed of this function and the 'fast' version
        """ predicts the active intentions of the human given the thresholds that are set for each intention. If for an
        intention, a threshold is defined, then the intention is only activated if the corresponding goal has a value
        larger than the threshold. In this function, the corresponding goal is taken from inputs of the selector, and
        checked if it is the one declared for the intention. This is safer than 'activate_intentions_by_threshold_fast'
        but requires (most likely) unnecessary checks.

        """
        self.deactivate_all_intentions()  # erase information about intentions
        for intention in self.outputs:
            self.activate_1_intention_by_threshold_fast(intention)

    def activate_1_intention_by_threshold(self, intention):
        """ activates one intention if the value of its goal is higher than the threshold. Does this in the most robust
        way, as described in the documentation of 'activate_intentions_by_threshold'

        Parameters
        ----------
        intention : lib.tom_model.model_elements.variables.dm_variables.IntentionThreshold
            the intention that will be checked
        """
        goal = next(var for var in self.inputs if var == intention.goal)
        belief = next((var for var in self.inputs if var == intention.belief), None)
        if belief is None:
            if is_value_over_threshold(goal.value, intention.threshold, intention.larger_than_threshold):
                self.activate_intention(intention)
        else:
            if is_value_over_threshold(goal.value,
                                       (intention.threshold + belief.value * intention.belief_contribution),
                                       intention.larger_than_threshold):
                self.activate_intention(intention)

    def deactivate_all_intentions(self):
        """ deactivates all the intentions of the intention selector.

        """
        self.active_intentions = []
        for intention in self.outputs:
            intention.deactivate()

    def activate_intention(self, intention):
        """ activates one intention, and adds it to the array of active intentions

        Parameters
        ----------
        intention :
            intention that will be deactivated
        """
        intention.activate()
        self.active_intentions.append(intention)

    def check_if_influencers_of_intentions_are_inputs(self):
        """ checks if the 'beliefs' and 'goals' associated to each 'intention' in 'self.outputs' are an input of the
        intention selector. This is important to run if function in usage is 'activate_intentions_by_threshold_fast'

        """
        for intention in self.outputs:
            assert intention.goal in self.inputs
            if intention.belief is not None:
                assert intention.belief in self.inputs


def is_value_over_threshold(value, threshold, larger_than_threshold=True):
    if larger_than_threshold:
        if value > threshold:
            return True
    else:
        if value < threshold:
            return True
    return False


class IntentionSelectorHighestGoal(IntentionSelector):
    def __init__(self, inputs, outputs, input_type=None, output_type=None):
        """ Child class of Intention Selector, where the intention associated with the goal with the highest value is
        triggered.

        Parameters
        ----------
        inputs :
        outputs :
        input_type :
        output_type :
        """
        input_type = (fst_dyn.Belief, fst_dyn.BeliefData, fst_dyn.Goal) if input_type is None else input_type
        output_type = dm_vars.Intention if output_type is None else output_type
        super().__init__(inputs, outputs, IntentionSelectorHighestGoal.highest_goal, input_type, output_type)

    def highest_goal(self):
        """ selects the intention that is associated with the goal with the highest value at the moment

        """
        all_goals = []
        for ele in self.inputs:
            if isinstance(ele, fst_dyn.Goal):
                all_goals.append(ele)
        current_goal = all_goals[0]
        for goal in all_goals:
            if goal.value >= current_goal.value:
                current_goal = goal
                for intention in self.outputs:
                    if intention.object_of_variable == goal.object_of_variable:
                        self.next_output = intention
