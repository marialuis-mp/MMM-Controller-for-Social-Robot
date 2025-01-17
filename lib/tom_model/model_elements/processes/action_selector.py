from abc import ABCMeta

import lib.tom_model.model_elements.variables.decision_making_variables
from lib.tom_model.model_elements.variables import fst_dynamics_variables as fst_dyn_vars, outer_variables
from lib.tom_model.model_elements.processes import process


class ActionSelector(process.DecisionMakingProcess):
    __metaclass__ = ABCMeta

    def __init__(self, inputs, outputs, function, input_type, output_type,
                 mode_predict_all=False, input_source=None):
        """ This is the general implementation of a ActionSelector class, the wnd process of decision-making module.
        A specific version of the ActionSelector (dependent on the application) must be implemented by deriving
        this class.

        Parameters
        ----------
        inputs : Inputs of the process
        outputs : Output of the process
        function : Function that is used to process the input(s) and create the output(s)
        input_type : Class of inputs allowed for the child class that specifies the process. For example, the input_type
            that is defined for the child class of ActionSelector (e.g., ActionSelectorHuman) could be
            IntentionOfHuman, since the ActionSelector receives as inputs objects of any child class of Intention.
        output_type : Class of outputs allowed for the child class that specifies the process
        mode_predict_all : if one optimal action is predicted or, in case there are multiple (equally) optimal actions,
            they are all given
        input_source :
        """
        super().__init__(inputs, outputs, function, input_type=input_type, output_type=output_type,
                         input_type_parent_class=(
                         lib.tom_model.model_elements.variables.decision_making_variables.Intention, fst_dyn_vars.Belief,
                         fst_dyn_vars.BeliefData),
                         output_type_parent_class=lib.tom_model.model_elements.variables.decision_making_variables.Action,
                         input_source=input_source)
        self.mode_predict_all = mode_predict_all    # if one action will be predicted or several

    def set_function(self, function):
        """ Sets the function that represents the process and checks whether it is allowed or not.

        Parameters
        ----------
        function : Method that represents the specified ActionSelector process. This function must be a method of a
        child class of the ActionSelector class (the specifically implemented ActionSelector child class that depends
        on the application).
        """
        if ActionSelector.__qualname__ in function.__qualname__:
            self.function = function
        else:
            raise TypeError('process function is not a method of this process class')
