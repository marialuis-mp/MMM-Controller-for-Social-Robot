import copy
import math
from abc import ABC, abstractmethod


class ReasoningPrepos:
    def __init__(self, function, name_input, pd, number_outputs):
        """ A reasoning preposition that represents the decoupled input-output relationships.
        Each ReasoningPrepos is linked to one input and has as many parameters as needed to represent the relationship
        of that input that each one of the output that the input influences.
        For each output, it translates the impact of the input on the output as a value through the function
        self.reason_function that is parameterized.

        Parameters
        ----------
        function : Union[experimentNao.declare_model.modules.reasoning_prepositions.PropSimpleFunction, experimentNao.declare_model.modules.reasoning_prepositions.ExpFunction]
        name_input : str
        pd : experimentNao.declare_model.modules.declare_perception_module.ChessPerceivedData
        number_outputs : int
        """
        self.reason_function = function
        self.name_input = name_input
        self.output_relationship = [None] * number_outputs
        self.perceived_data = pd

    def add_output_relationship(self, output_number):
        """ associates another output relationship to this reasoning preposition

        Parameters
        ----------
        output_number : int
        """
        self.output_relationship[output_number] = copy.deepcopy(self.reason_function)

    def add_parameter(self, output_number, par_value, par_number):
        """ adds a parameter to an output relationship. If the output relationship does not exist yet, it creates it first.

        Parameters
        ----------
        output_number : int
        par_value : Union[int, float, numpy.float64]
        par_number : int
        """
        if self.output_relationship[output_number] is None:
            self.add_output_relationship(output_number)
        self.output_relationship[output_number].set_parameter_value(par_value, par_number)

    def get_value_of_reasoning_inf_on_output(self, output_number_tag):
        """ returns a value that reflects the impact/influence of the input on the output. Computed through the function
        self.reason_function that is parameterized.

        Parameters
        ----------
        output_number_tag : int

        Returns
        -------
        numpy.float64
        """
        return self.output_relationship[output_number_tag].function(self.get_value_input())

    def get_value_input(self):
        """ returns the current value of the input (perceived data) - e.g., n_hints=2, returns 2

        Returns
        -------
        Union[numpy.int64, int]
        """
        if self.name_input != 'n_wrong_attempts':
            return getattr(self.perceived_data.data, self.name_input, 'Do not exist')
        else:
            return sum(getattr(self.perceived_data.data, self.name_input, 'Do not exist'))

    def bound_parameter_value(self, param_value, param_number=0):
        """ makes sure that the value of the parameter is bounded in the allowed range

        Parameters
        ----------
        param_value : float
        param_number : int

        Returns
        -------

        """
        range_of_param = self.reason_function.output_relationship[param_number].ranges
        return min(max(param_value, range_of_param[0]), range_of_param[1])


class ReasoningFunction(ABC):
    def __init__(self, parameters):
        """ mathematically relates each input of the rational reasoning to one output

        Parameters
        ----------
        parameters : list[Parameter]
        """
        self.number_parameters = len(parameters)
        self.parameters = []
        for par in parameters:
            assert isinstance(par, Parameter)
            self.parameters.append(par)

    @abstractmethod
    def function(self, value):
        """ the mathematical function that relate each input of the rational reasoning to one output

        Parameters
        ----------
        value :
        """
        pass

    def set_parameter_value(self, param_value, param_number):
        """ sets the value of one parameter of the mathematical function

        Parameters
        ----------
        param_value :
        param_number :
        """
        self.parameters[param_number].set_value(param_value)


class PropFunction(ReasoningFunction):
    def __init__(self, x_domain):
        super().__init__(parameters=[Parameter((2, 2)), Parameter((-1, 1))])
        self.x_domain = x_domain

    def function(self, value):
        value = value/self.x_domain
        return self.parameters[0].value * value + self.parameters[1].value


class PropPosFunction(PropFunction):    # Proportional positive function
    def __init__(self, x_domain):
        ReasoningFunction.__init__(self, parameters=[Parameter((0, 2)), Parameter((-1, 1))])
        self.x_domain = x_domain


class PropSimpleFunction(PropPosFunction):    # Proportional positive function
    def __init__(self, x_domain):
        ReasoningFunction.__init__(self, parameters=[Parameter((0, 2))])
        self.x_domain = x_domain

    def function(self, value):
        value = value/self.x_domain
        return self.parameters[0].value * value


class ATanFunction(ReasoningFunction):
    def __init__(self):
        super().__init__(parameters=[Parameter((-0.7, 0.7)), Parameter((0.01, 1)), Parameter((0, 20))])

    def function(self, value):
        return self.parameters[0].value*math.atan(self.parameters[1].value * value - self.parameters[2].value)


class LogFunction(ReasoningFunction):
    def __init__(self):
        super().__init__(parameters=[Parameter((-1, 1)), Parameter((-1, 1))])

    def function(self, value):
        return math.log(value + self.parameters[0].value, self.parameters[1].value)


class ExpFunction(ReasoningFunction):
    def __init__(self, x_domain):
        # super().__init__(parameters=[Parameter((-2, -0.1)), Parameter((-2.5, 0))])    - without normalization
        super().__init__(parameters=[Parameter((-2, 0)), Parameter((-1, 1))])
        self.x_domain = x_domain

    def function(self, value):
        theta_1 = -1 * pow(10, self.parameters[1].value)
        value = value / self.x_domain
        return self.parameters[0].value * math.exp(theta_1 * value) + 1


class BoolFunction(ReasoningFunction):
    def __init__(self):
        super().__init__(parameters=[])

    def function(self, value: bool):
        return 1 if value else -1


class BoolFunctionParam(ReasoningFunction):
    def __init__(self, n_parameters=1, special_case1=False, special_case2=False):
        parameters = [Parameter((0, 1)) for i in range(n_parameters)]
        super().__init__(parameters=parameters)
        self.special_case_1 = special_case1  # return -1 * self.parameters[0].value when false
        self.special_case_2 = special_case2  # returns 0 when false

    def function(self, value: bool):
        if len(self.parameters) == 1:
            if not self.special_case_1:
                return self.parameters[0].value if value else -1 * self.parameters[0].value
            if not self.special_case_2:
                return self.parameters[0].value if value else 0
            else:
                return self.parameters[0].value if value else -1
        else:
            return self.parameters[0].value if value else -1 * self.parameters[1].value


class Parameter:
    def __init__(self, ranges: tuple, value=0):
        """ parameters of the ReasoningFunction functions

        Parameters
        ----------
        ranges : Tuple[int, int]
        value : int
        """
        self.value = value
        self.ranges = ranges

    def set_value(self, value):
        """ sets value of the parameter

        Parameters
        ----------
        value : Union[int, float, numpy.float64]
        """
        self.value = self.bound_parameter_value(value)

    def bound_parameter_value(self, param_value):
        """ bounds the value of the parameter inside the ranges

        Parameters
        ----------
        param_value : Union[int, float, numpy.float64]

        Returns
        -------
        Union[int, float, numpy.float64]
        """
        return min(max(param_value, self.ranges[0]), self.ranges[1])
