from experimentNao.model_ID.cognitive import perception_beliefs_ID as percept_ID
from lib.algorithms.gradient_descent import parameters2optimise as params
from lib.tom_model.model_elements.linkage import influencer, scheduled_weight
from lib.tom_model.model_elements.variables import slow_dynamics_variables as slw_dyn, fst_dynamics_variables as fst_dyn


class ParametersManager:
    def __init__(self, tom_model, random, include_slow_dyn, include_cognitive=True, include_perception=True):
        """ manages the parameters being identified in the identification of the tom model

        Parameters
        ----------
        tom_model : experimentNao.declare_model.declare_entire_model.ToMModelChessSimpleDyn
            model whose parameters must be identified
        random : random.Random
            the random variable (for traceability)
        include_slow_dyn : bool
            if the slow dynamic state variables are going to be identified as parameters or not
        include_cognitive : bool
            whether the parameters of the cognitive model are to be identified
        include_perception : bool
            whether the parameters of the perception model are to be identified
        """
        self.parameters_counter = 0
        self.tom_model = tom_model
        self.include_slow_dyn = include_slow_dyn
        self.random = random
        self._include_cognitive = include_cognitive
        self._include_perception = include_perception

    @property
    def include_cognitive(self):
        return self._include_cognitive

    @include_cognitive.setter
    def include_cognitive(self, value):
        self._include_cognitive = value

    @property
    def include_perception(self):
        return self._include_perception

    @include_perception.setter
    def include_perception(self, value):
        self._include_perception = value

    # ************************************************* Initialization *************************************************
    def initialize_parameters(self, vars_w_links_w_id, settings):
        """ initialise the parameters of the model, linked with the variables "vars_w_links_w_id"

        Parameters
        ----------
        vars_w_links_w_id : Union[Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]]
        settings : lib.algorithms.gradient_descent.settings.Settings

        Returns
        -------
        List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]
        """
        parameters2optimise = []
        self.parameters_counter = 0
        if self.include_cognitive:
            self.initialize_parameters_cognitive(vars_w_links_w_id, settings, parameters2optimise)
        if self.include_perception:
            self.initialize_parameters_perception(vars_w_links_w_id, parameters2optimise)
        return parameters2optimise

    def initialize_parameters_cognitive(self, vars_w_links_w_id, settings, parameters2optimise):
        """ initializes the parameters of the cognitive module linked with variables "vars_w_link_w_id", adding them
        to "parameters2optimise"

        Parameters
        ----------
        vars_w_links_w_id : Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion]
        settings : lib.algorithms.gradient_descent.settings.Settings
        parameters2optimise : List
        """
        self.iterate_through_params_of_cognt_mdl(parameters2optimise, vars_w_links_w_id,
                                                 lambda array, v, inf, j, ranges_=settings.get_range_values():
                                                 self.add_1_parameter(array, v, inf, ranges_, j))

    def initialize_parameters_perception(self, vars_w_links_w_id, parameters2optimise):
        """ iterates through the parameters of the perception module linked with variables "vars_w_link_w_id",
        initializes them, and adds them to "parameters2optimise"

        Parameters
        ----------
        vars_w_links_w_id : Union[Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]]
        parameters2optimise : Union[List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise], List]
        """
        self.iterate_through_params_of_percept_mdl(parameters2optimise, vars_w_links_w_id,
                                                   self.add_perception_params_of_1_belief)

    # ********************************************** Set values of params **********************************************
    def set_values_of_parameters(self, parameters2optimise, vars_w_links_to_id):
        """ sets the values of the parameters "parameters2optimise" into their place on the cognitive module.
        Only parameters associated with variables "vars_w_links_to_id" are considered.

        Parameters
        ----------
        parameters2optimise : List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]
        vars_w_links_to_id : Union[Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]]
        """
        self.parameters_counter = 0
        if self.include_cognitive:
            self.iterate_through_params_of_cognt_mdl(parameters2optimise, vars_w_links_to_id, self.set_value_of_1_par)
        if self.include_perception:
            self.iterate_through_params_of_percept_mdl(parameters2optimise, vars_w_links_to_id,
                                                       self.set_values_of_perception_params_of_1_belief)

    # ****************************************** Get information from params *******************************************
    def get_information_of_parameters(self, vars_w_links_w_id, df_params_list):
        """ Get information of the parameters associated with variables "vars_w_links_to_id" are considered. The
        information includes the number of the parameters in the sequence of parameters, and the type and name of both
        the influenced and influencer variables.

        Parameters
        ----------
        vars_w_links_w_id : Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]
        df_params_list : pandas.core.frame.DataFrame
        """
        parameters2optimise = []
        self.parameters_counter = 0
        if self.include_cognitive:
            self.iterate_through_params_of_cognt_mdl(parameters2optimise, vars_w_links_w_id,
                                                     lambda array, v, inf, j, df=df_params_list:
                                                     self.get_info_of_1_parameter_cog(array, v, inf, j, df))
        if self.include_perception:
            self.iterate_through_params_of_percept_mdl(parameters2optimise, vars_w_links_w_id,
                                                       self.add_perception_params_of_1_belief)
            for i in range(len(parameters2optimise)):   # parameters2optimise only has the params from cognitive
                df_params_list.loc[len(df_params_list.index)] = [str(self.parameters_counter + i),  # add perception params
                                                                 'RLD: ' + parameters2optimise[i].name,
                                                                 'PK: ' + parameters2optimise[i].var_or_linkage_represented.name]

    # *****************  Apply initialization, setting values, or getting information to 1 parameter  ******************
    def add_1_parameter(self, parameters2optimise, influenced_var, influencer_of_par, range_values, j):
        """ Initializes one parameter and adds it to "parameter2optimise".

        Parameters
        ----------
        parameters2optimise : Union[List, List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]]
        influenced_var : Union[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias]
        influencer_of_par : lib.tom_model.model_elements.linkage.influencer.Influencer
        range_values : Tuple[int, int]
        j : int
        """
        if isinstance(influencer_of_par, influencer.Influencer):
            name = 'Link ' + str(influencer_of_par.influencer_variable.tag) + '->' + str(influenced_var.tag)
            var = influencer_of_par.influencer_linkage
            range_values = influencer_of_par.boundary_values
        elif isinstance(influencer_of_par, slw_dyn.SlowDynamicsVariable):
            name, var = 'Slow Dyn - ' + influencer_of_par.name, influencer_of_par
            range_values = (0, 1)
        parameters2optimise.append((params.Parameter2Optimise(*range_values, value=self.random.uniform(*range_values),
                                                              var_or_linkage_represented=var, name=name)))
        self.parameters_counter += 1

    def set_value_of_1_par(self, parameters2optimise, influenced_var, influencer_of_par, j):
        """ Sets the value of one parameter (getting the value from position "j" of "parameters2optimise").

        Parameters
        ----------
        parameters2optimise : List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]
        influenced_var : Union[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias]
        influencer_of_par : lib.tom_model.model_elements.linkage.influencer.Influencer
        j : int
        """
        if isinstance(influencer_of_par, influencer.Influencer):
            if isinstance(influencer_of_par.influencer_linkage, scheduled_weight.ScheduledWeight):
                influencer_of_par.influencer_linkage.weights[j] = parameters2optimise[self.parameters_counter].value
            else:
                influencer_of_par.influencer_linkage = parameters2optimise[self.parameters_counter].value
        elif isinstance(influencer_of_par, slw_dyn.SlowDynamicsVariable):
            influencer_of_par.value = parameters2optimise[self.parameters_counter].value
        self.parameters_counter += 1

    def get_info_of_1_parameter_cog(self, parameters2optimise, influenced_var, influencer_of_par, j, df):
        """ returns the information associated with the parameter pointed by the counter "self.parameters_counter".

        Parameters
        ----------
        parameters2optimise : List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]
        influenced_var : Union[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias]
        influencer_of_par : lib.tom_model.model_elements.linkage.influencer.Influencer
        j : int
        df : pandas.DataFrame
        """
        influencer_var = influencer_of_par.influencer_variable if isinstance(influencer_of_par, influencer.Influencer) \
            else influencer_of_par
        df.loc[len(df.index)] = [str(self.parameters_counter),
                                 influencer_var.get_name_of_type()[0] + ': ' + influencer_var.name,
                                 influenced_var.get_name_of_type()[0] + ': ' + influenced_var.name]
        self.parameters_counter += 1

    def add_perception_params_of_1_belief(self, parameters2optimise, belief):
        """ Initializes all the parameters of the perception module associated with this "belief" and adds them to
        "parameter2optimise".

        Parameters
        ----------
        parameters2optimise : Union[List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise], List]
        belief : Union[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]
        """
        parameters2optimise.extend(percept_ID.initialize_params_of_perception(self.tom_model.perception_module, belief,
                                                                              self.random))

    def set_values_of_perception_params_of_1_belief(self, parameters2optimise, belief):
        """ Sets the values of the parameters of the perception module associated with this "belief". The values of the
        parameters come from "parameters2optimise", and are the N contiguous position, starting in position
        "self.parameters_counter", where N is the amount of parameters associated with the "belief".

        Parameters
        ----------
        parameters2optimise : List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]
        belief : Union[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]
        """
        n_params_of_output = percept_ID.set_params_of_perception(self.tom_model.perception_module, belief,
                                                                 parameters2optimise, self.parameters_counter)
        self.parameters_counter += n_params_of_output

    # ******************************************  Iterate over parameters  *******************************************
    def iterate_through_params_of_cognt_mdl(self, parameters2optimise, vars_w_links_w_id, to_do_to_params):
        """ iterates through the parameters of the cognitive module, applying the function "to_do_to_params" to them.

        Parameters
        ----------
        parameters2optimise : Union[List, List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]]
        vars_w_links_w_id : Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion]
        to_do_to_params : Union[function, method]
            function that will be applied to the parameters
        """
        for fst_dyn_var in vars_w_links_w_id:
            for inf in fst_dyn_var.influencers:
                if not isinstance(inf.influencer_variable, fst_dyn.Bias):
                    self.iterate_through_params_of_1_inf(parameters2optimise, fst_dyn_var, inf, to_do_to_params)
        if self.include_slow_dyn:
            for slw_dyn_var in self.tom_model.cognitive_module.get_all_slow_dynamics_vars():
                to_do_to_params(parameters2optimise, slw_dyn_var, slw_dyn_var, 0)

    @staticmethod
    def iterate_through_params_of_1_inf(parameters2optimise, var, inf, to_do_to_params):
        """ iterates through the parameters associated with one influencer "inf" of the variable "var",
         applying the function "to_do_to_params" to them.

        Parameters
        ----------
        parameters2optimise : Union[List, List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]]
        var : Union[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias]
        inf : lib.tom_model.model_elements.linkage.influencer.Influencer
        to_do_to_params : Union[function, method]
        """
        if isinstance(inf.influencer_linkage, scheduled_weight.ScheduledWeight):
            for j in range(len(inf.influencer_linkage.weights)):
                to_do_to_params(parameters2optimise, var, inf, j)
        else:
            to_do_to_params(parameters2optimise, var, inf, 0)

    @staticmethod
    def iterate_through_params_of_percept_mdl(parameters2optimise, vars_w_links_w_id, to_do_to_params):
        """ iterates through the parameters of the perception module, applying the function "to_do_to_params" to them.

        Parameters
        ----------
        parameters2optimise : Union[List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise], List]
        vars_w_links_w_id : Union[Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]]
        to_do_to_params : method
        """
        for var in vars_w_links_w_id:
            if isinstance(var, fst_dyn.Belief) or isinstance(var, fst_dyn.PerceivedKnowledge):
                to_do_to_params(parameters2optimise, var)

    def change_included_vars(self, include_cognitive, include_perception):
        """ change the group of variables that are considered in the parameters management

        Parameters
        ----------
        include_cognitive : bool
        include_perception : bool
        """
        self.include_cognitive = include_cognitive
        self.include_perception = include_perception

    def count_parameters(self, vars_w_links_w_id, settings):
        """ counts the number of parameters being managed by the parameter manager

        Parameters
        ----------
        vars_w_links_w_id : Union[Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]]
        settings : lib.algorithms.gradient_descent.settings.Settings

        Returns
        -------

        """
        parameters2optimise = []
        self.parameters_counter = 0
        self.initialize_parameters_cognitive(vars_w_links_w_id, settings, parameters2optimise)
        self.initialize_parameters_perception(vars_w_links_w_id, parameters2optimise)
        n_parameters_cog = self.parameters_counter
        n_parameters_percept = len(parameters2optimise) - n_parameters_cog
        return n_parameters_percept, n_parameters_cog


