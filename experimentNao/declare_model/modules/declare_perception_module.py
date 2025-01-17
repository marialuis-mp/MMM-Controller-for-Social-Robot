import lib.tom_model.model_elements.variables.perception_variables
from experimentNao.declare_model import chess_interaction_data
from experimentNao.declare_model.modules.reasoning_prepositions import ReasoningPrepos, PropFunction,  BoolFunctionParam, BoolFunction, ExpFunction, PropPosFunction, PropSimpleFunction
from lib.algorithms.gradient_descent.parameters2optimise import Parameter2Optimise
from lib.tom_model.model_elements.processes import perceptual_access, rational_reasoning


class ChessRLD(lib.tom_model.model_elements.variables.perception_variables.RealLifeData):
    def __init__(self, name: str, data: chess_interaction_data.ChessInteractionData):
        """ Real life data in the interaction of playing chess games with Nao

        Parameters
        ----------
        name : str
        data : experimentNao.declare_model.chess_interaction_data.ChessInteractionData
        """
        super().__init__(name, data)
        self.sequence_of_inputs = []
        self.current_input_in_seq = None

    def add_input_to_sequence_of_inputs(self, new_input: chess_interaction_data.ChessInteractionData):
        """ adds one rld input to the sequence of inputs (useful to train the model)

        Parameters
        ----------
        new_input : experimentNao.declare_model.chess_interaction_data.ChessInteractionData
        """
        self.sequence_of_inputs.append(new_input)

    def set_current_input_from_sequence(self, tag):
        """ sets the current input as the input number 'tag' from the sequence of inputs

        Parameters
        ----------
        tag : int
        """
        self.data = self.sequence_of_inputs[tag]
        self.current_input_in_seq = tag
        
    def set_next_input_from_sequence(self):
        """ sets the current input as the next input. If the previous input was the "n" position of the sequence of
        inputs, then the new input will be the "n+1" position

        """
        self.current_input_in_seq += 1
        self.data = self.sequence_of_inputs[self.current_input_in_seq]

    def set_data(self, data):
        """ sets the current input as the argument "data"

        Parameters
        ----------
        data : experimentNao.declare_model.chess_interaction_data.ChessInteractionData
        """
        assert isinstance(data, chess_interaction_data.ChessInteractionData)
        self.data = data


class ChessPerceivedData(lib.tom_model.model_elements.variables.perception_variables.PerceivedData):
    def __init__(self, name: str, data: chess_interaction_data.ChessInteractionData):
        """ Perceived data in the interaction of playing chess games with Nao

        Parameters
        ----------
        name : str
        data : experimentNao.declare_model.chess_interaction_data.ChessInteractionData
        """
        super().__init__(name, data)


class ChessRationallyPerceivedKnowledge(lib.tom_model.model_elements.variables.perception_variables.PerceivedKnowledgeSet):
    def __init__(self, name: str, raw_data, knowledge):
        """ Rationally Perceived Knowledge in the interaction of playing chess games with Nao

        Parameters
        ----------
        name : str
        raw_data : experimentNao.declare_model.chess_interaction_data.ChessInteractionData
        knowledge : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.RationallyPerceivedKnowledge]
        """
        super().__init__(name, raw_data, knowledge)


class HumanPerceptualAccess(perceptual_access.PerceptualAccess):
    def __init__(self, inputs, outputs):
        """ Perceptual access in the interaction of playing chess games with Nao

        Parameters
        ----------
        inputs : experimentNao.declare_model.modules.declare_perception_module.ChessRLD
        outputs : experimentNao.declare_model.modules.declare_perception_module.ChessPerceivedData
        """
        super().__init__(inputs, outputs, function=self.one,
                         input_type=ChessRLD, output_type=ChessPerceivedData)

    def one(self):
        """ defines the perceived data as the real life data (assumes perfect observation)

        """
        self.next_outputs.data = self.inputs.data


class HumanRationalReasoning(rational_reasoning.RationalReasoning):
    def __init__(self, inputs, outputs, included_vars, max_values_rld):
        """ Rational Reasoning in the interaction of playing chess games with Nao. Defines the rational reasoning as the
        sum of decoupled input-output processes.
        1) First, set of reasoning prepositions is defined, each one linked to one input of this module (perceived data).
        2) Then, for each output of the module (rpk), a copy of each preposition linked to an input that influences
        that output is made. The output is computed by summing these copy of the prepositions.
        3) Each copy of preposition (which represents a pair input-output) as its own parameters which are identified.

        Parameters
        ----------
        inputs : experimentNao.declare_model.modules.declare_perception_module.ChessPerceivedData
        outputs : experimentNao.declare_model.modules.declare_perception_module.ChessRationallyPerceivedKnowledge
        included_vars : experimentNao.declare_model.included_elements.IncludedElements
        max_values_rld : Union[Dict[str, int], Dict[str, float], Dict[str, float], Dict[str, float], Dict[str, float], Dict[str, float]]
        """
        super().__init__(inputs, outputs, function=self.run_rational_reasoning,
                         input_type=ChessPerceivedData, output_type=ChessRationallyPerceivedKnowledge)
        self.reasoning_prep = None
        self.outputs_info = None
        self.set_reasoning_prepositions(max_values_rld, included_vars.nonlinear_perception, included_vars.simplified_perception)
        self.set_output_info(included_vars)
        self.number_of_parameters = []
        for output in self.outputs.knowledge:
            self.number_of_parameters.append(self.get_number_of_parameters_of_1_output(output))
            self.set_parameters_of_1_output(output, [0]*self.number_of_parameters[-1])
        OutputInfo.counter = 0  # for new copies of the model, the counter of OutputInfo should be reset

    def set_reasoning_prepositions(self, max_values, nonlinear=True, simplified=True):
        """ sets the reasoning prepositions, where each one is linked to one input of this module (perceived data).

        Parameters
        ----------
        max_values : Union[Dict[str, int], Dict[str, float], Dict[str, float], Dict[str, float], Dict[str, float], Dict[str, float]]
        nonlinear : bool
        simplified : bool
        """
        prop_f = PropSimpleFunction if simplified else PropPosFunction
        non_lin_f = ExpFunction if nonlinear else prop_f
        self.reasoning_prep = (self.get_reasoning_preposition('n_hints', prop_f, max_values),                     # 0
                               self.get_reasoning_preposition('n_wrong_attempts', non_lin_f, max_values),         # 1
                               self.get_reasoning_preposition('puzzle_difficulty', prop_f, max_values),           # 2
                               self.get_reasoning_preposition('proportion_of_moves_revealed', PropFunction, max_values),
                               self.get_reasoning_preposition('time_2_solve', non_lin_f, max_values),             # 4
                               self.get_reasoning_preposition_bool('nao_helping', BoolFunctionParam(1, True)),    # 5
                               self.get_reasoning_preposition_bool('nao_offering_rewards', BoolFunction()),       # 6
                               self.get_reasoning_preposition_bool('reward_given', BoolFunction()),               # 7
                               self.get_reasoning_preposition_bool('skipped_puzzle', BoolFunctionParam(2)))       # 8

    def get_reasoning_preposition(self, input_name, function_type, max_values_rld):
        """ declares a reasoning proposition linked to a perceived data "input_name", with a specific "function_type",
        and a maximum value

        Parameters
        ----------
        input_name : str
        function_type : abc.ABCMeta
        max_values_rld : Union[Dict[str, int], Dict[str, float], Dict[str, float], Dict[str, float], Dict[str, float], Dict[str, float]]

        Returns
        -------
        experimentNao.declare_model.modules.reasoning_prepositions.ReasoningPrepos
        """
        reasoning_function = function_type(max_values_rld[input_name])
        return ReasoningPrepos(reasoning_function, input_name, self.inputs, number_outputs=len(self.outputs.knowledge))

    def get_reasoning_preposition_bool(self, input_name, function_type):
        """ declares a specific type of reasoning proposition linked to a bolean perceived data "input_name", with a
        specific "function_type"

        Parameters
        ----------
        input_name : str
        function_type : Union[experimentNao.declare_model.modules.reasoning_prepositions.BoolFunctionParam, experimentNao.declare_model.modules.reasoning_prepositions.BoolFunction]

        Returns
        -------
        experimentNao.declare_model.modules.reasoning_prepositions.ReasoningPrepos
        """
        return ReasoningPrepos(function_type, input_name, self.inputs, number_outputs=len(self.outputs.knowledge))

    def set_output_info(self, included_vars):
        """ Declares the information of each output of the module, specifically, which inputs are linked to it (aka which
        reasoning proposition are linked to it), and the function used to add the reasoning propositions, and the name
        of the output

        Parameters
        ----------
        included_vars : experimentNao.declare_model.included_elements.IncludedElements
        """
        self.outputs_info = (OutputInfo([0, 1, 2, 4, 8], self.compute_pk, 'game difficulty'), )
        if included_vars.belief_nao_helping:
            self.outputs_info = self.outputs_info + (OutputInfo([0, 5], self.compute_nao_helping_pk, 'nao helping'), )
        if included_vars.belief_made_progress:
            self.outputs_info = self.outputs_info + (OutputInfo([3, 4], self.compute_pk, 'made progress'),)
        if included_vars.belief_reward:
            if included_vars.belief_reward_hidden:
                self.outputs_info = self.outputs_info + (OutputInfo([7], self.compute_pk, 'nao offering rewards'),)
            else:
                self.outputs_info = self.outputs_info \
                                    + (OutputInfo([6, 7], self.compute_nao_rewarding_pk, 'nao offering rewards'), )

    def get_output_info(self, output):
        """ returns the information of a specific output of the module

        Parameters
        ----------
        output : lib.tom_model.model_elements.variables.fst_dynamics_variables.RationallyPerceivedKnowledge

        Returns
        -------
        Tuple[List[int], int, method]
        """
        output_info = next((output_info for output_info in self.outputs_info if output_info.name == output.name), None)
        return output_info.get_output_info()

    def get_number_of_parameters_of_1_output(self, output):
        """ returns the total number of parameters of all the reasoning preposition associated with one output

        Parameters
        ----------
        output : lib.tom_model.model_elements.variables.fst_dynamics_variables.RationallyPerceivedKnowledge

        Returns
        -------
        int
        """
        perceived_data, output_number, function = self.get_output_info(output)
        number_parameters = 0
        for inf in perceived_data:
            number_parameters += self.reasoning_prep[inf].reason_function.number_parameters
        return number_parameters

    def set_parameters_of_1_output(self, output_var, parameters_values):
        """ sets the parameters 1 output, by settings the parameters of all the reasoning prepositions linked to that
        one output.

        Parameters
        ----------
        output_var : lib.tom_model.model_elements.variables.fst_dynamics_variables.RationallyPerceivedKnowledge
        parameters_values : Union[List[int], List, List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]]
        """
        influencers, output_number, function = self.get_output_info(output_var)
        for inf in influencers:
            self.reasoning_prep[inf].add_output_relationship(output_number)
        self.iterate_through_parameters_of_1_output(parameters_values, output_var, self.set_1_parameter_value)

    def initialize_parameters_of_1_output(self, output_var, random):
        """ initializes the parameters of all the reasoning prepositions linked to one output.

        Parameters
        ----------
        output_var : lib.tom_model.model_elements.variables.fst_dynamics_variables.RationallyPerceivedKnowledge
        random : random.Random

        Returns
        -------
        List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]
        """
        parameters_values = []
        self.iterate_through_parameters_of_1_output(parameters_values, output_var,
                                                    lambda ps, pc, o_n, i_n, p_n, random_=random:
                                                    self.initialize_1_parameter(ps, pc, o_n, i_n, random, p_n))
        return parameters_values

    def set_1_parameter_value(self, params: list, par_counter: int, output_number: int, inf_number: int,
                              par_number: int):
        """

        Parameters
        ----------
        params : Union[List[int], List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]]
            array with parameters values
        par_counter : int
            position of the parameter in the array of parameters of the output. Useful for the optimisation process
        output_number : int
            position of the output in the array of outputs of the RationalReasoning
        inf_number : int
            number of the influencer in the array of inputs [influencers] of the RationalReasoning
        par_number :
            position of the parameter in the array of parameters of the connection between the influencer and the output
        """
        par_value = params[par_counter].value if isinstance(params[par_counter], Parameter2Optimise) else params[par_counter]
        self.reasoning_prep[inf_number].add_parameter(output_number, par_value, par_number)

    def initialize_1_parameter(self, parameters, params_counter, output_number, input_number, random, param_number=0):
        range_values = self.reasoning_prep[input_number].output_relationship[output_number].parameters[param_number].ranges
        parameters.append((Parameter2Optimise(*range_values, value=random.uniform(*range_values),
                                              var_or_linkage_represented=self.outputs.knowledge[output_number],
                                              name=self.reasoning_prep[input_number].name_input)))

    def iterate_though_parameters(self, parameter_values, function_todo):
        """

        Parameters
        ----------
        parameter_values : Union[List[int], List, List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]]
        function_todo :

        Returns
        -------

        """
        j = 0
        for output in self.outputs.knowledge:
            j = self.iterate_through_parameters_of_1_output(parameter_values, output, function_todo, j)
        return j

    def iterate_through_parameters_of_1_output(self, parameters_values, output, function_todo, params_counter=0):
        """

        Parameters
        ----------
        parameters_values : Union[List[int], List, List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]]
        output : lib.tom_model.model_elements.variables.fst_dynamics_variables.RationallyPerceivedKnowledge
        function_todo : Union[method, function]
        params_counter : int

        Returns
        -------
        int
        """
        influencers, output_number, function = self.get_output_info(output)
        for inf in influencers:
            n_params_per_output = self.reasoning_prep[inf].reason_function.number_parameters
            if n_params_per_output == 1:    # if influencer has 1 param per output
                function_todo(parameters_values, params_counter, output_number, inf, 0)
                params_counter += 1
            else:
                for i in range(n_params_per_output):
                    function_todo(parameters_values, params_counter, output_number, inf, i)
                    params_counter += 1
        return params_counter

    def compute_pk(self, influencers, this_output_number_tag):
        """ computes the value of a piece of perceived knowledge

        Parameters
        ----------
        influencers : List[int]
        this_output_number_tag : int

        Returns
        -------
        numpy.float64
        """
        value = 0
        for i in influencers:
            value += self.reasoning_prep[i].get_value_of_reasoning_inf_on_output(this_output_number_tag)
        return value

    def compute_nao_helping_pk(self, influencers, this_output_number_tag):
        """ computes the value of piece of perceived knowledge "nao_helping"

        Parameters
        ----------
        influencers :
        this_output_number_tag :

        Returns
        -------

        """
        value = 1
        for i in influencers:
            value = value * self.reasoning_prep[i].get_value_of_reasoning_inf_on_output(this_output_number_tag)
        return value

    def compute_nao_rewarding_pk(self, influencers, this_output_number_tag):
        """ computes the value of piece of perceived knowledge "nao_rewarding"

        Parameters
        ----------
        influencers :
        this_output_number_tag :

        Returns
        -------

        """
        value = self.compute_pk(influencers, this_output_number_tag)
        return value/2

    def run_rational_reasoning(self):
        """ runs the module of the RationalReasoning, computing each output one-by-one

        """
        for output in self.outputs.knowledge:
            self.run_rational_reasoning_1_output(output)

    def run_rational_reasoning_1_output(self, output):
        """ computes and updates the value of one output (one piece of RationallyPerceivedKnowledge) of the module

        Parameters
        ----------
        output : lib.tom_model.model_elements.variables.fst_dynamics_variables.RationallyPerceivedKnowledge
        """
        influencers, output_number, function = self.get_output_info(output)
        value = function(influencers, output_number)
        output.next_value = value


def get_default_max_values():
    """ gets the default maximum values of the real life data, in case there is no data from the participants

    Returns
    -------
    Dict[str, int]
    """
    return {'n_hints': 5, 'n_wrong_attempts': 50, 'puzzle_difficulty': 5,
            'proportion_of_moves_revealed': 1, 'time_2_solve': 200}


class OutputInfo:
    counter = 0

    def __init__(self, perceived_data, function, name):
        """ Stores the information of each output of the module, specifically:
        1) the list of inputs that are linked to it (aka which reasoning proposition are linked to it), in terms of
        their positions in the reasoning propositions list
        2) the function used to add the reasoning propositions
        3) the name of the output

        Parameters
        ----------
        perceived_data : List[int]
        function : method
        name : str
        """
        self.name = name
        self.perceived_data = perceived_data
        self.output_number = OutputInfo.counter
        self.function = function
        OutputInfo.counter += 1

    def get_output_info(self):
        """ returns information about this output

        Returns
        -------
        Tuple[List[int], int, method]
        """
        return self.perceived_data, self.output_number, self.function
