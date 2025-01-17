import copy

import lib.tom_model.model_elements.variables.perception_variables
from lib.tom_model.model_elements.processes import process
from lib.tom_model.model_elements.variables import fst_dynamics_variables, outer_variables


class RationalReasoning(process.PerceptionProcess):
    def __init__(self, inputs, outputs, function, input_type, output_type):
        """ This is the general implementation of the Rational Reasoning, the 2nd process of the modules module.
        A specific version of the RationalReasoning (dependent on the application) must be implemented by deriving this
        class. This is a derived class from PerceptionProcess.

        Parameters
        ----------
        inputs : Inputs of the process
        outputs : Output of the process
        function : Function that is used to process the input(s) and create the output(s)
        input_type : Class of inputs allowed for the child class that specifies the process. For example, the input_type
         that is defined for the child class of Rational Reasoning (e.g., RationalReasoningHuman) could be
         PerceivedDataHuman, since the RationalReasoning receives as input objects of any child class of PerceivedData.
        output_type : Class of outputs allowed for the child class that specifies the process
        """
        super().__init__(inputs, outputs, function, input_type=input_type, output_type=output_type,
                         input_type_parent_class=lib.tom_model.model_elements.variables.perception_variables.PerceivedData,
                         output_type_parent_class=lib.tom_model.model_elements.variables.perception_variables.PerceivedKnowledgeSet)

    def compute_new_value(self):
        # Since there are two types of outputs --> we have to update them differently
        self.next_outputs.raw_data = copy.deepcopy(self.outputs.raw_data)
        self.function()

    def update_value(self):
        self.outputs.raw_data.__dict__ = self.next_outputs.raw_data.__dict__
        for pk in self.outputs.knowledge:
            assert isinstance(pk, fst_dynamics_variables.FastDynamicsVariable)
            pk.update_value()

    def set_function(self, function):
        """ Sets the function that represents the process and checks whether it is allowed or not.

        Parameters
        ----------
        function : Method that represents the specified rational reasoning process. This function must be a method of a
        derived class of the main RationalReasoning class (the specifically implemented RationalReasoning child class
        that depends on the application)
        """
        if RationalReasoning.__qualname__ in function.__qualname__:
            self.function = function
        else:
            raise TypeError('process function is not a method of this process class')

    def get_pks(self):
        return self.outputs.knowledge

    def get_output_raw_data(self):
        return self.outputs.raw_data
