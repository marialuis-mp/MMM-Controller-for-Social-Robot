from lib.algorithms.gradient_descent.parameters2optimise import Parameter2Optimise


class ParametersManagerDM:
    def __init__(self, settings, boundary_values, random):
        """  manages the parameters being identified in the identification of the dm module

        Parameters
        ----------
        settings : lib.algorithms.genetic_algorithm.settings.Settings
        boundary_values : Tuple[int, int]
        random : random.Random
        """
        self.parameters_counter = 0
        self.boundary_values = boundary_values
        self.settings = settings
        self.random = random

    def initialize_parameters(self, intentions):
        """ initialises the parameters of the model, linked with the "intentions"

        Parameters
        ----------
        intentions : List[experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame]

        Returns
        -------
        List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]
        """
        parameters = []
        parameters = self.iterate_through_parameters(intentions, parameters,
                                                     lambda p, i, t: self.add_1(p, i, t))
        return parameters

    def set_values_of_thresholds(self, intentions, parameters):
        """ Sets the values of the parameters "parameters", which correspond to the thresholds of the dm module.
        Only parameters associated with variables "intentions" are considered.

        Parameters
        ----------
        intentions : List[experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame]
        parameters : List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]
        """
        self.iterate_through_parameters(intentions, parameters, self.set_value_of_1_par)

    def iterate_through_parameters(self, intentions, parameters, function_2_apply):
        """ iterates through the parameters of the dm module, applying the function "function_2_apply" to them.

        Parameters
        ----------
        intentions : List[experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame]
        parameters : Union[List, List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]]
        function_2_apply : Union[function, method]

        Returns
        -------
        List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]
        """
        self.parameters_counter = 0
        for intention in intentions:
            function_2_apply(parameters, intention, True)
            if intention.belief is not None:
                function_2_apply(parameters, intention, False)
        return parameters

    def add_1(self, parameters2opt, intention, threshold: bool):
        """ Initializes one parameter and adds it to "parameters2opt".

        Parameters
        ----------
        parameters2opt : List
        intention : experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame
        threshold : bool
        """
        name = intention.name + (' threshold' if threshold else ' belief contrib')
        parameters2opt.append((Parameter2Optimise(*self.boundary_values, value=self.random.uniform(*self.boundary_values),
                                                  var_or_linkage_represented=intention, name=name)))
        self.parameters_counter += 1

    def set_value_of_1_par(self, parameters2opt, intention, threshold: bool):
        """  Sets the value of one parameter (the parameter corresponding to the "intention").

        Parameters
        ----------
        parameters2opt : List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]
        intention : experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame
        threshold : bool
        """
        if threshold:
            intention.threshold = parameters2opt[self.parameters_counter].value
        else:
            intention.belief_contribution = parameters2opt[self.parameters_counter].value
        self.parameters_counter += 1

    def get_n_params_and_runs(self, intentions):
        """ returns the number of parameters associated with a group of intentions "intentions" and the number of runs
        that are estimated to be needed to identify these parameters.

        Parameters
        ----------
        intentions : List[experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame]

        Returns
        -------

        """
        n_params = len(self.initialize_parameters(intentions))          # with many parameters, we need more runs
        n_runs = min(max(self.settings.min_n_runs, n_params ** 2), self.settings.max_n_runs)
        return n_params, n_runs


def set_parameters(parameters_df, dm_module):
    """ Sets the values of the parameters of the dm module

    Parameters
    ----------
    parameters_df : pandas.DataFrame
    dm_module : lib.tom_model.model_structure.decision_making_module.DecisionMakingModule
    """
    parameters_manager = ParametersManagerDM(None, (-1, 1), None)
    for intention in dm_module.intention_selector.outputs:
        parameters_of_intention = []
        for par in range(len(parameters_df)):  # find parameters of intention
            if intention.name in parameters_df.iloc[par]['Name of parameter']:
                parameters_of_intention.append(Parameter2Optimise(-1, 1, value=parameters_df.iloc[par]['Value']))
        parameters_manager.set_values_of_thresholds((intention, ), parameters_of_intention)
