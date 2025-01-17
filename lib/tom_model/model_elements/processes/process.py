import copy
import random
from abc import ABCMeta, abstractmethod, ABC


class Process:
    __metaclass__ = ABCMeta

    def __init__(self, inputs, outputs, function, input_type, output_type,
                 input_type_parent_class, output_type_parent_class):
        """ Metaclass that represents all processes in the ToM model_structure. Processes are functions that receive 1
        or more cognitive variables as inputs, process them, and produce another variables as outcome.

        Parameters
        ----------
        inputs : Variables that are the input(s) of the process
        outputs : Variables that are the output(s) of the process
        function : Function that is used to process the input(s) and create the output(s)
        input_type : Class of inputs allowed for the child class that specifies the process. E.g., the input_type that
            is defined for the child class of Perceptual Access (a derived PerceptualAccess) could be RealLifeDataNao)
        output_type : Class of outputs allowed for the child class that specifies the process
        input_type_parent_class : General (parent) classes allowed as inputs for the type of process. E.g., for a
            Perceptual Access (parent class) process, the input type must be a child class of
            Real Life Data (RealLifeData is the input_type_parent_class).
        output_type_parent_class : General (parent) classes allowed as outputs of the type of process
        """
        self.input_type = input_type
        self.output_type = output_type
        self.check_input_or_output_type(self.input_type, input_type_parent_class)
        self.check_input_or_output_type(self.output_type, output_type_parent_class)
        self.inputs = []
        self.outputs = []
        self.set_input(inputs)
        self.set_output(outputs)
        self.inputs = tuple(self.inputs)
        self.outputs = tuple(self.outputs)
        self.function = None
        self.set_function(function)
        self.values = []    # if necessary, to store values chosen through the episode

    @abstractmethod
    def set_function(self, function):
        pass

    def set_input(self, inputs):
        """ Add each element in "inputs" to the list of inputs of the process. If any element is a list/tuple, the
        function is called again.

        Parameters
        ----------
        inputs :
            inputs to be added. Each individual input to be added must be of the type predefined for the inputs of
            the current Process
        """
        if isinstance(inputs, self.input_type):
            self.inputs.append(inputs)
        elif isinstance(inputs, (tuple, list)):
            for ele in inputs:
                self.set_input(ele)
        else:
            raise TypeError('Input ', inputs, ' is not of right type (pre-declared for this process)')

    def set_output(self, outputs):
        """ Add each element in "outputs" to the list of outputs of the process. If any element is a list/tuple, the
        function is called again.

        Parameters
        ----------
        outputs : outputs to be added. Each individual output to be added must be of the type predefined for the outputs
            of the current Process
        """
        if isinstance(outputs, self.output_type):
            self.outputs.append(outputs)
        elif isinstance(outputs, list):
            for ele in outputs:
                self.set_output(ele)
        else:
            raise TypeError('Output ', outputs, ' is not of right type (pre-declared for this process)')

    def check_input_or_output_type(self, input_or_output_type, input_or_output_type_parent_class):
        """ Checks whether the input or output types that are defined for a process P that is a child class of
        Process Type PT are of the right classes for that type of process PT

        Parameters
        ----------
        input_or_output_type : type
            The type of the inputs or output of process P that is a child of process type PT
        input_or_output_type_parent_class : type
            Parent classes allowed for the inputs or output of process P that is a child of process type PT
        """
        if isinstance(input_or_output_type, (list, tuple)):
            for input_type in input_or_output_type:
                if not issubclass(input_type, input_or_output_type_parent_class):
                    raise TypeError(self.get_warning_string(input_type.__name__, input_or_output_type_parent_class))
        elif not issubclass(input_or_output_type, input_or_output_type_parent_class):
            raise TypeError(self.get_warning_string(input_or_output_type.__name__, input_or_output_type_parent_class))

    def get_warning_string(self, input_type_name, input_type_parent_class):
        return 'Input type ' + input_type_name + ' is not allowed for a ' + self.__class__.__bases__[0].__name__ \
               + ' child class. The input classes should be a child class of ' + input_type_parent_class.__name__ + '.'

    def compute_new_value(self):
        """ Computes the new value of the outputs of the process, i.e., executes the process.

        """
        self.function()


class PerceptionProcess(Process):
    def __init__(self, inputs, outputs, function, input_type, output_type,
                 input_type_parent_class, output_type_parent_class):
        """ More specific processes that are part of the modules module

        Parameters
        ----------
        inputs : Inputs of the process
        outputs : Output of the process
        function : Function that is used to process the input(s) and create the output(s)
        input_type : Class of inputs allowed for the child class that specifies the process. For example, the input_type
         that is defined for the child class of Perceptual Access (a derived PerceptualAccess) could be RealLifeDataNao)
        output_type : Class of outputs allowed for the child class that specifies the process
        input_type_parent_class : General (parent) classes allowed as inputs for the type of process. For example, for a
            PerceptualAccess specific process (i.e., a child class of PerceptualAccess), the input type must be a
            child class of RealLifeData (RealLifeData is the input_type_parent_class).
        output_type_parent_class : General (parent) classes allowed as outputs of the type of process
        """
        super().__init__(inputs, outputs, function, input_type, output_type,
                         input_type_parent_class, output_type_parent_class)
        if len(self.inputs) == 1:
            self.inputs = self.inputs[0]
        if len(self.outputs) == 1:
            self.outputs = self.outputs[0]   # The outputs correspond to the values of all the outputs in the current k
        # the next_outputs are the value of the outputs that are computed for the next time step
        self.next_outputs = copy.deepcopy(self.outputs)

    @abstractmethod
    def set_function(self, function):
        pass

    def compute_new_value(self):
        """ Computes new values of the outputs by running the function that corresponds to the process. The current
        values of the outputs are copied to the next outputs, and the next_outputs are then overwritten by
        self.function(). After this, the next_outputs have the outputs of the next time step, but the self.outputs were
        not yet updated. This can be done with "update_value()".

        """
        self.next_outputs = copy.deepcopy(self.outputs)     # this line might be redundant, but I kept it for safety
        self.function()

    def update_value(self):
        """ Updates the values of the all the outputs with what had been computed to be the next values of the outputs.
        Returns
        -------
        object

        """
        self.outputs.__dict__ = self.next_outputs.__dict__


class DecisionMakingProcess(Process):
    def __init__(self, inputs, outputs, function, input_type, output_type,
                 input_type_parent_class, output_type_parent_class, input_source=None):
        """ More specific processes that are part of the decision-making module

        Parameters
        ----------
        inputs : Inputs of the process
        outputs : Output of the process
        function : Function that is used to process the input(s) and create the output(s)
        input_source : the process that is sequentially right before self (if any). The output of this input_source
        process is the input of self.
        input_type : Class of inputs allowed for the child class that specifies the process (e.g., the input_type that
            is defined for the child class of Intention Selector (e.g., IntentionSelectorHuman) could be BeliefOfHuman)
        output_type : Class of outputs allowed for the child class that specifies the process
        input_type_parent_class : General (parent) classes allowed as inputs for the type of process. For example, for a
            IntentionSelector specific process (i.e., a child class of IntentionSelector), the input type must be a
            child class of Belief or Goal (Belief and Goal are the input_type_parent_class).
        output_type_parent_class : General (parent) classes allowed as outputs of the type of process
        """
        super().__init__(inputs, outputs, function, input_type, output_type,
                         input_type_parent_class, output_type_parent_class)
        self.current_output = random.choice(outputs)        # current output is a subset of the possible outputs
        self.next_output = None                             # the "chosen" output for the next time step (before update)
        self.input_source = input_source

    @abstractmethod
    def set_function(self, function):
        pass

    def compute_new_value(self):
        """ Computes new values of the outputs by running the function that corresponds to the process. The current
        values of the outputs are copied to the next outputs, and the next_outputs are then overwritten by
        self.function(). After this, the next_outputs have the outputs of the next time step, but the self.outputs were
        not yet updated. This can be done with "update_value()".

        """
        self.next_output = copy.copy(self.current_output)
        self.function(self)

    def update_value(self):
        """ Updates the current output with the output element that been selected to be the next output.
         Returns
         -------
         object

         """
        self.current_output = copy.copy(self.next_output)
