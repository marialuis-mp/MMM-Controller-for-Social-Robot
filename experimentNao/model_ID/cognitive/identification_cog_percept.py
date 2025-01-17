import time

import pandas as pd

from experimentNao.model_ID.cognitive import identification_cog_all_module as id_all, parameters_manager as pm
from experimentNao.model_ID.configs import id_cog_modes
from experimentNao.model_ID.data_processing import excel_data_processing as edp
from experimentNao.model_ID.data_processing import optimisation_data_processing as odp
from lib import excel_files
from lib.tom_model.model_elements.variables.fst_dynamics_variables import RationallyPerceivedKnowledge, \
    PerceivedKnowledge


class CognitiveIdPercept(id_all.CognitiveIdAll):
    def __init__(self, tom_model, n_puzzles, writer_files, reader_files, prune, included_vars, random, overall_id_config,
                 short_mode, verbose, delft_blue=False, reuse_data_sep_3=True):
        """  identification system that identifies the parameters of multiple groups of variables at once, but separates
        the identification of the perception and cognition.

        Parameters
        ----------
        tom_model : experimentNao.declare_model.declare_entire_model.ToMModelChessSimpleDyn
        n_puzzles : List[int]
        writer_files : pandas.io.excel._openpyxl.OpenpyxlWriter
        reader_files : List[pandas.io.excel._base.ExcelFile]
        prune : bool
        included_vars : experimentNao.declare_model.included_elements.IncludedElements
        random : random.Random
        overall_id_config : experimentNao.model_ID.configs.overall_config.IDConfig
        short_mode : bool
        verbose : int
        delft_blue : bool
        reuse_data_sep_3 : bool
        """
        super().__init__(tom_model, n_puzzles, writer_files, reader_files, prune, included_vars, random,
                         overall_id_config, short_mode, verbose, delft_blue=delft_blue)
        self.parameters_manager = pm.ParametersManager(self.tom_model, random, self.include_slow_dyn,
                                                       include_cognitive=False)
        self.n_runs_perception = 10 if short_mode else 100
        self.currently_iding_only_perception = True
        self.final_gd_adjustment = False
        self.overall_df_number = 1
        self.opt_perception_parameters = None
        self.opt_cognitive_parameters = None
        self.conservative_train_steps = None
        self.conservative_test_steps = None
        self.per_sep_1_df = []
        if reuse_data_sep_3:   # This is useful, if the SEP_PER_1 was already run and SEP_PER_3 is being run
            self.get_df_for_sep_per_3() # since it the first part of SEP_PER_3 is the same as inn SEP_PER_1

    def identify_and_test(self):
        """ runs the identification and testing of the tom model. runs the sequence of the identification depending on
        the self.id_mode.

        """
        self.set_train_and_test_data()
        if self.id_mode == id_cog_modes.IdCogModes.SEP_PER_1:
            self.get_conservative_time_steps()
            self.identify_and_test_perception_part()
            self.identify_and_test_cognition_part()
        elif self.id_mode == id_cog_modes.IdCogModes.SEP_PER_2:
            self.identify_and_test_perception_part()
            self.identify_and_test_w_warm_start_only_perception()
        elif self.id_mode == id_cog_modes.IdCogModes.SEP_PER_3:
            if len(self.per_sep_1_df) == 0:     # if reuse_data_sep_3 was False, repeat step of SEP_PER_1
                self.identify_and_test_perception_part()
                self.identify_and_test_cognition_part()
            else:
                self.extract_opt_parameters_from_per_sep_1_df()
            self.identify_and_test_w_warm_start_all()
        self.post_process_id_and_test()

    def identify_and_test_perception_part(self):
        """ manages the identification and testing of the perception module alone.

        """
        print('\n************* Identifying perception alone *************')
        vars_2_id = self.tom_model.cognitive_module.get_beliefs()
        self.identify_perception_part(vars_2_id)
        self.test_perception_part(vars_2_id)
        self.parameters_manager.set_values_of_parameters(self.opt_perception_parameters, vars_2_id)
        self.currently_iding_only_perception = False

    def identify_and_test_cognition_part(self):
        """ manages the identification and testing of the cognitive module alone.

        """
        print('\n************* Identifying cognition alone *************')
        self.parameters_manager.change_included_vars(include_cognitive=True, include_perception=False)
        self.identify()     # identify cognition
        self.overall_df_number = 1
        self.test_cognitive_part()

    def identify_and_test_w_warm_start_only_perception(self):
        """ manages the identification and testing of the perception module alone while setting the initial values of
        the parameters of the perception module with a warm start.

        """
        print('\n************* Identifying all with warm start in perception *************')
        self.parameters_manager.change_included_vars(include_cognitive=True, include_perception=True)
        self.warm_start_perception_params = self.opt_perception_parameters
        self.identify()  # identify cognition and perception
        self.test(position_in_dfs=1)

    def identify_and_test_w_warm_start_all(self):
        """ manages the identification and testing of the perception module and cognitive module while setting the
        initial values of parameters with a warm start.

        """
        print('\n************* Identifying all with warm start *************')
        sheet_name = 'ID final'
        self.currently_iding_only_perception = False
        self.final_gd_adjustment = True
        self.parameters_manager.change_included_vars(include_cognitive=True, include_perception=True)
        self.warm_start_perception_params = self.opt_perception_parameters
        self.settings.initial_learning_rate = 0.01
        self.settings.learning_rate_decay = -0.01
        self.settings.differentiation_step = 0.01
        self.settings.max_differentiation_step = 0.01
        self.settings.n_iterations = 150
        for params in self.opt_cognitive_parameters:
            self.warm_start_cognitive_params = params
            self.identify(sheet_name=sheet_name)  # identify cognition and perception
        self.post_process_id_w_warm_start_all()
        self.test(position_in_dfs=self.overall_df_number, sheet_name=sheet_name)

    def post_process_id_and_test(self):
        # attach_debugger()
        n_params_percept, n_params_cog = self.parameters_manager.count_parameters(self.vars_w_linkages_to_id, self.settings)
        ttl_n_params = n_params_percept + n_params_cog
        if self.id_mode == id_cog_modes.IdCogModes.SEP_PER_3:
            if len(self.per_sep_1_df) == 0:
                self.df_params_list = self.df_params_list.iloc[:2*ttl_n_params]
            else:
                self.df_params_list = self.df_params_list.tail(n_params_percept + n_params_cog)
        self.get_list_of_parameters_4_excel()
        # reduce list of parameters
        self.df_params_list = self.df_params_list.tail(n_params_percept + n_params_cog)
        edp.write_list_of_parameters_2_excel(self.writer, self.df_params_list)
        overall_performance_df = self.prepare_overall_performance_data()
        excel_files.save_df_to_excel_sheet(self.writer, overall_performance_df, 'Overall Performance')

    def identify_perception_part(self, vars_2_id):
        """ identifies the parameters of the perception module only.

        Parameters
        ----------
        vars_2_id : Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]
        """
        train_steps = self.train_steps if self.conservative_train_steps is None else self.conservative_train_steps
        self.identify_set_of_variables(vars_2_id,
                                       lambda params, ts=train_steps, pm=self.parameters_manager, v2id=vars_2_id,
                                              tm=self.tom_model, nh=self.n_horizon, sp=self.overall_id_config.simple_dynamics:
                                       cost_function_perception(params, ts, pm, v2id, tm, nh, sp),
                                       sheet_name='ID Perception')

    def test_perception_part(self, vars_2_id):
        """ tests the outcome of the identification process of the perception module only. This is done by running the
        cost function on the testing data using the identified parameters of the perception module.

        Parameters
        ----------
        vars_2_id : Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]
        """
        test_steps = self.test_steps if self.conservative_test_steps is None else self.conservative_test_steps
        test_costs = self.test_set_of_vars(vars_2_id,
                                           lambda params, ts=test_steps, pm=self.parameters_manager,
                                                  v2id=vars_2_id, tm=self.tom_model, nh=self.n_horizon,
                                                  sp=self.overall_id_config.simple_dynamics:
                                           cost_function_perception(params, ts, pm, v2id, tm, nh, sp),
                                           position_in_dfs=0, sheet_name='ID Perception')
        self.opt_perception_parameters = self.get_set_of_parameters_that_generated_test_cost(0, test_costs, min(test_costs))
        print('\ttest costs: ', test_costs, '\n\topt parameters: ', self.opt_perception_parameters)

    def test_cognitive_part(self):
        """ tests the outcome of the identification process of the cognition module only. This is done by running the
        cost function on the testing data using the identified parameters of the cognitive module

        """
        position_in_dfs = 1
        ttl_costs_test = self.test(position_in_dfs)
        self.opt_cognitive_parameters = []
        for test_cost in ttl_costs_test:
            params = self.get_set_of_parameters_that_generated_test_cost(position_in_dfs, ttl_costs_test, test_cost)
            self.opt_cognitive_parameters.append(params)
            print('\ttest costs: ', test_cost, '\n\topt parameters: ', self.opt_perception_parameters[-1])

    def post_process_id_w_warm_start_all(self):
        """ post process of the training, before testing, for the case when all the parameters of the model were
        identified from previous warm starts (id_mode=SEP_PER_3)

        """
        n_optimal_sets = len(self.opt_cognitive_parameters)
        self.overall_df_number = 2 if len(self.per_sep_1_df) == 0 else 0
        current_df = self.dfs_everything[self.overall_df_number]
        current_df = current_df.head(3)
        for i in range(1, n_optimal_sets):
            current_df = pd.concat([current_df, self.dfs_everything[self.overall_df_number + i].iloc[[-1]]])
            self.dfs_optimal_sets[self.overall_df_number] = pd.concat([self.dfs_optimal_sets[self.overall_df_number],
                                                                       self.dfs_optimal_sets[self.overall_df_number + i]])
        identified_params = odp.find_identified_parameters(current_df.tail(n_optimal_sets), list(range(n_optimal_sets)))
        identified_params = [None] + identified_params
        current_df.iloc[1] = identified_params + [None] * (len(current_df.columns) - len(identified_params))
        self.dfs_everything[self.overall_df_number] = current_df
        self.dfs_everything = self.dfs_everything[:self.overall_df_number+1]

    def get_set_of_parameters_that_generated_test_cost(self, position_in_dfs, test_costs_all, test_cost):
        """ finds the set of parameters that generated a specific test cost

        Parameters
        ----------
        position_in_dfs : int
        test_costs_all : List[numpy.float64]
        test_cost : numpy.float64

        Returns
        -------
        List[float]
        """
        set_with_min_test_cost = test_costs_all.index(test_cost)  # set of parameters with minimum test cost
        row_in_df = set_with_min_test_cost + 2                      # row in df corresponding to this set
        assert self.dfs_everything[position_in_dfs]['Test cost'].iloc[row_in_df] == test_costs_all[set_with_min_test_cost]
        return get_set_of_params_in_a_row(self.dfs_everything[position_in_dfs], row_in_df)

    def get_number_of_runs(self, n_parameters):
        if self.currently_iding_only_perception:
            return self.n_runs_perception
        elif self.final_gd_adjustment:
            return 1
        else:
            return self.settings.default_n_runs

    def get_number_of_identified_parameters(self, df_everything_number):
        identified_params, n_params = 0, 0
        dfs_to_consider = self.dfs_everything if self.id_mode == id_cog_modes.IdCogModes.SEP_PER_1 \
            else [self.dfs_everything[self.overall_df_number]]
        for df in dfs_to_consider:
            for column in df.columns:
                if 'Param' in column:
                    identified_params += 1 if df.iloc[1][column] else 0
                    n_params += 1
        return identified_params, n_params

    def extract_opt_parameters_from_per_sep_1_df(self):
        """ selects the set of optimal parameters from the document generated when identification was run with
        self.id_mode=SEP_PER_1 (if "reuse_data_sep_3" was True in the constructor).

        """
        test_cost_name = 'Test cost'
        n_params_percept, n_params_cog = self.parameters_manager.count_parameters(self.vars_w_linkages_to_id, self.settings)
        df_percept = self.per_sep_1_df[0]
        df_cog = self.per_sep_1_df[1]
        df_percept = (df_percept[df_percept[test_cost_name].notna()]).reset_index(drop=True)
        df_cog = (df_cog[df_cog[test_cost_name].notna()]).reset_index(drop=True)
        # Perception
        self.opt_perception_parameters = get_set_of_params_in_a_row(df_percept, df_percept[test_cost_name].idxmin())
        assert len(self.opt_perception_parameters) == n_params_percept
        # Cognition
        self.opt_cognitive_parameters = []
        for i in range(len(df_cog)):
            params = get_set_of_params_in_a_row(df_cog, i)
            assert len(params) == n_params_cog
            self.opt_cognitive_parameters.append(params)
        pass

    def get_df_for_sep_per_3(self):
        """ fills self.per_sep_1_df to be reused in SEP_PER_3. This is useful if the SEP_PER_1 was already run and
        SEP_PER_3 is being run, since it the first part of SEP_PER_3 is the same as inn SEP_PER_1.

        """
        if self.id_mode == id_cog_modes.IdCogModes.SEP_PER_3:
            try:
                self.per_sep_1_df = edp.open_results_from_sep_per_1(self.overall_id_config)
            except FileNotFoundError:
                self.per_sep_1_df = []

    def get_conservative_time_steps(self):
        """ Returns the time steps where the emotions are not very extreme (i.e., are close to 0) to identify the
        perception. In these time steps, the bias is negligible, and the approximation of the bias being null can be
        made. This allows identifying the perception under the assumption that the bias is null and the rationally
        perceived knowledge is the same as the belief.

        """
        relevant_emotions = self.get_emotions_that_influence_biases()
        self.conservative_train_steps = self.select_conservative_time_steps_of_a_kind(relevant_emotions, self.train_steps,
                                                                                      self.overall_id_config.simple_dynamics)
        self.conservative_test_steps = self.select_conservative_time_steps_of_a_kind(relevant_emotions, self.test_steps,
                                                                                     self.overall_id_config.simple_dynamics)
        percentage_train_ok = len(self.conservative_train_steps) / len(self.train_steps)
        percentage_test_ok = len(self.conservative_test_steps) / len(self.test_steps)
        if percentage_train_ok < 0.5 or percentage_test_ok < 0.5:
            print('\nATTENTION: Not using conservative training steps for PER SEP 1!\n')
            self.conservative_train_steps = None
            self.conservative_test_steps = None

    def get_emotions_that_influence_biases(self):
        """ returns a list of the variables that influence the biases (and consequently the beliefs) of the model

        Returns
        -------

        """
        relevant_emotions = []
        for bias in self.tom_model.cognitive_module.biases:
            for inf in bias.influencers:
                if inf.influencer_variable not in relevant_emotions:
                    relevant_emotions.append(inf.influencer_variable)
        return relevant_emotions

    def select_conservative_time_steps_of_a_kind(self, relevant_emotions, steps, simplified_dynamics):
        """  Returns the time steps where the emotions are not very extreme (i.e., are close to 0) from a pool of steps
        (either training or test)

        Parameters
        ----------
        relevant_emotions : List[lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion]
        steps : List[int]
        simplified_dynamics : bool

        Returns
        -------
        List
        """
        conservative_steps = []
        for step in steps:
            conservative_step = True
            k = convert_train_data_step_in_time_step(step, self.n_horizon, simplified_dynamics)
            for emotion in relevant_emotions:
                if abs(emotion.values[k]) >= 0.5:    # -0.4 until 0.4
                    conservative_step = False
                    break
            if conservative_step:
                conservative_steps.append(step)
        return conservative_steps


def get_set_of_params_in_a_row(df, row_in_df):
    """ get the values of the parameters of the row "row_in_df" from a data frame with the format that is the same as
    the output dataframe of an interaction "row_in_df" (i.e., df with columns: final cost + parameters values + the
    cost values per iteration)

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
    row_in_df : int

    Returns
    -------
    List[float]
    """
    set_of_parameters = list()
    for column in list(df.columns):
        if 'param' in column.lower():
            set_of_parameters.append(df[column].iloc[row_in_df])
    return set_of_parameters


def cost_function_perception(parameters_2_id, training_steps, parameters_manager, vars_2_id, tom_model, n_horizon,
                             simplified_dynamics):
    """ the cost function for the identification of the perception module

    Parameters
    ----------
    parameters_2_id : List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]
    training_steps : List[int]
    parameters_manager : experimentNao.model_ID.cognitive.parameters_manager.ParametersManager
    vars_2_id : Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]
    tom_model : experimentNao.declare_model.declare_entire_model.ToMModelChessSimpleDyn
    n_horizon : int
    simplified_dynamics : bool

    Returns
    -------
    numpy.float64
    """
    parameters_manager.set_values_of_parameters(parameters_2_id, vars_2_id)
    cost = 0
    for training_step in training_steps:  # k = this_train_step
        k = convert_train_data_step_in_time_step(training_step, n_horizon, simplified_dynamics)
        tom_model.perception_module.perceptual_access.inputs.set_current_input_from_sequence(k)
        tom_model.perception_module.compute_and_update_module_in_1_go()
        if simplified_dynamics:
            for pk in tom_model.cognitive_module.pk:
                pk.compute_variable_value()
                pk.update_value()
        for belief in vars_2_id:  # vars 2 id are beliefs
            pk = next((i.influencer_variable for i in belief.influencers if isinstance(i.influencer_variable,
                                                                                       (RationallyPerceivedKnowledge,
                                                                                        PerceivedKnowledge))))
            cost += (belief.values[k] - pk.value) ** 2
    return cost


def convert_train_data_step_in_time_step(training_step, n_horizon, simplified_dynamics):
    """ makes the conversion between a training data step (1, 2, 3, 4. etc...) in the k of the controller time.
    These two steps are only different when te dynamics are not simplified (simplified_dynamics=False)

    Parameters
    ----------
    training_step : int
    n_horizon : int
    simplified_dynamics : bool

    Returns
    -------
    int
    """
    # time step equivalent to the training step
    if simplified_dynamics:     # if simplified -> different
        return training_step
    else:
        return n_horizon * training_step + 1
