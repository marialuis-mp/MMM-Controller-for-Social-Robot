import lib.tom_model.model_elements.variables.perception_variables
from lib.tom_model.model_elements.processes import process


class PerceptualAccess(process.PerceptionProcess):
    def __init__(self, inputs, outputs, function, input_type, output_type):
        """ This is the general implementation of the Perceptual access, the 1st process of modules module.
        A specific version of the PerceptualAccess (dependent on the application) must be implemented by deriving this class.
        This is a derived class from PerceptionProcess.

        Parameters
        ----------
        inputs : Inputs of the process
        outputs : Output of the process
        function : Function that is used to process the input(s) and create the output(s)
        input_type : Class of inputs allowed for the child class that specifies the process. For example, the input_type
         that is defined for the child class of Perceptual Access (e.g., PerceptualAccessNao) could be RealLifeDataNao,
         since the PerceptualAccess receives as input objects of any child class of Real Life Data.
        output_type : Class of outputs allowed for the child class that specifies the process
        """
        super().__init__(inputs, outputs, function, input_type=input_type, output_type=output_type,
                         input_type_parent_class=lib.tom_model.model_elements.variables.perception_variables.RealLifeData,
                         output_type_parent_class=lib.tom_model.model_elements.variables.perception_variables.PerceivedData)

    def set_function(self, function):
        """ Sets the function that represents the process and checks whether it is allowed or not.

        Parameters
        ----------
        function : Method that represents the specified perceptual access process. This function must be a method of a
        child class of the PerceptualAccess class (the specifically implemented PerceptualAccess child class that
        depends on the application)
        """
        if PerceptualAccess.__qualname__ in function.__qualname__:
            self.function = function
        else:
            raise TypeError('process function is not a method of this process class')
