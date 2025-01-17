import copy
import math
import time
import multiprocess as mp

import pandas as pd

from lib import excel_files
from lib.algorithms.gradient_descent.settings import Settings
from lib.algorithms.gradient_descent import gradient_descent_opt as gd
from experimentNao.model_ID.cognitive import parameters_manager as pm
from experimentNao.model_ID.cognitive import set_values_of_variables_cog as set_values_cog
from experimentNao.model_ID.configs import train_test_config
from experimentNao.model_ID.data_processing import excel_data_processing, optimisation_data_processing as data, \
    pick_train_data


class CognitiveIdentification:
    def __init__(self, tom_model, n_puzzles, writer_files, reader_files, prune, random, overall_id_config,
                 short_mode=False, verbose=0, multiprocess=True, include_slow_dyn=False, delft_blue=False):
        """ identification system that identifies all the variables of the cognitive model at once. See parent class
        for description of parameters.

        Parameters
        ----------
        tom_model : experimentNao.declare_model.declare_entire_model.ToMModelChessSimpleDyn
            theory of mind model of the participant
        n_puzzles : List[int]
            number of puzzles that were played by the player in each session. Each element of the list corresponds to
            one session
        writer_files : pandas.io.excel._openpyxl.OpenpyxlWriter
            file to where the results are written to
        reader_files : List[pandas.io.excel._base.ExcelFile]
            output files of the training session, which correspond to the train and test data
        prune : bool
        random : random.Random
            the random variable (for traceability)
        overall_id_config : experimentNao.model_ID.configs.overall_config.IDConfig
            configuration of the identification process
        short_mode : bool
            shorter mode of the identification process, for debugging purposes
        verbose : int
            amount of output written to the console
        multiprocess : bool
            whether identification purpose can be run in multiple, parallel processes or not
        include_slow_dyn : bool
            if the slow dynamic state variables are going to be identified as parameters or not
        delft_blue : bool
            whether the programme is being run in the supercomputer (set as False, for users outside the TU Delft)
        """
        self.tom_model = tom_model
        self.n_puzzles = n_puzzles
        self.prune = prune
        self.with_multiprocess = multiprocess
        self.include_slow_dyn = include_slow_dyn
        self.writer, self.readers = writer_files, reader_files
        self.overall_id_config = overall_id_config
        self.verbose = verbose
        self.state_vars = None
        self.hidden_vars = []
        self.settings = None
        self.train_steps, self.test_steps = None, None
        self.dfs_optimal_sets = []      # dataframes with the best costs (and respective set of parameters)
        self.dfs_everything = []        # dataframes with all the identification data
        self.df_params_list = pd.DataFrame(columns=('Param number', 'Influencer', 'Influenced'))
        self.n_horizon = overall_id_config.n_horizon if overall_id_config.simple_dynamics else 2
        self.set_settings(short_mode=short_mode)
        self.id_engine = CognitiveIDEngine(self.settings, verbose)
        self.parameters_manager = pm.ParametersManager(self.tom_model, random, include_slow_dyn)
        excel_data_processing.write_list_of_vars_and_id_tags_2_excel(self.tom_model, self.writer)
        self.arguments_for_multi_processing = None
        self.random = random
        self.number_of_multiprocesses = 4 if not delft_blue else 24
        self.warm_start_perception_params = None
        self.warm_start_cognitive_params = None

    def set_settings(self, short_mode=False):
        """ defines the settings and hyperparameters for the identification

        Parameters
        ----------
        short_mode : bool
        """
        self.with_multiprocess = self.with_multiprocess if not short_mode else False
        n_iterations = 120 if not short_mode else 5
        default_n_runs = 250 if not short_mode else 6
        if self.overall_id_config.incremental:
            if self.overall_id_config.simple_dynamics:
                initial_learn_rate = 0.01 if self.n_horizon == 1 else 0.005
            else:
                initial_learn_rate = 0.001
        else:
            initial_learn_rate = 0.02
        s = Settings(n_iterations=n_iterations,
                     initial_learning_rate=initial_learn_rate, changing_learning_rate=True, learning_rate_decay=-0.005,
                     default_number_of_runs=default_n_runs, min_number_of_runs=20, max_number_of_runs=600,
                     prune_by_epsilon=True, epsilon=0.001, prune_half_time=self.prune, prune_half_time_error=0.25,
                     differentiation_step=0.01, max_differentiation_step=0.01, verbose=0, boundary_values=(-1, 1),
                     multiprocess=False, compute_cost_at_end_of_iteration=True, write_to_excel=False)
        self.settings = s

    def identify_and_test(self):
        """ runs the identification and testing of the tom model

        """
        self.set_train_and_test_data()
        self.identify()
        self.test()
        self.post_process_id_and_test()

    def identify_set_of_variables(self, vars_w_link_to_id, cost_function, sheet_name):
        """ identifies a set of variables 'vars_w_link_to_id'

        Parameters
        ----------
        vars_w_link_to_id : list[lib.tom_model.model_elements.variables.fst_dynamics_variables.FastDynamicsVariable]
            the list of variables of to identify
        cost_function : function
        sheet_name : str
        """
        parameters_2_id, n_parameters, n_runs, df, optimal_cost = self.pre_process_identification(vars_w_link_to_id)
        print('Number of parameters: {}'.format(n_parameters))
        if not self.with_multiprocess:  # sequential run
            for i in range(n_runs):
                optimal_cost = self.id_engine.run_one_gd(i, n_runs, vars_w_link_to_id, optimal_cost, cost_function, df,
                                                         self.parameters_manager, self.warm_start_perception_params,
                                                         self.warm_start_cognitive_params)
        else:   # multiprocess run
            optimal_cost, df = self.perform_id_with_multi(vars_w_link_to_id, cost_function, n_runs, df, optimal_cost)
        self.output_overall_information_of_identification(vars_w_link_to_id, df, parameters_2_id, sheet_name)

    def perform_id_with_multi(self, vars_w_link_to_id, cost_function, n_runs, df, optimal_cost, batch_size=30):
        """ performs the identification when there are multiprocesses

        Parameters
        ----------
        vars_w_link_to_id : list[lib.tom_model.model_elements.variables.fst_dynamics_variables.FastDynamicsVariable]
            the list of variables that have linkages to identify
        cost_function : function
        n_runs : int
            number of independent runs that the identification process must be ran
        df : pandas.DataFrame
            the dataframe that will hold the results
        optimal_cost : float
            initialized value of the optimal cost
        batch_size : int
            how many independent runs are performed in one batch, before the results  are written to the Excel file.
            A larger batch size results in a faster identification, but there is a higher risk of loosing data if
            the programme stops for any reason.

        Returns
        -------

        """
        randoms = []
        for y in range(n_runs):           # generate random objects that are traceable but different from each other
            self.random.random()
            randoms.append(copy.deepcopy(self.random))
        for j in range(math.ceil(n_runs / batch_size)):     # run id
            range_of_runs = range(batch_size * j, min(batch_size * (j + 1), n_runs))
            with mp.Pool(min(n_runs, self.number_of_multiprocesses)) as pool:
                results = pool.starmap(one_run_of_gd_multi, [(i, n_runs, vars_w_link_to_id, optimal_cost, cost_function,
                                                              pd.DataFrame(columns=df.columns), self.settings,
                                                              self.verbose, self.tom_model, randoms[i],
                                                              self.parameters_manager.include_cognitive,
                                                              self.parameters_manager.include_perception,
                                                              self.include_slow_dyn, self.warm_start_perception_params,
                                                              self.warm_start_cognitive_params) for i in range_of_runs])
                for result in results:
                    df = pd.concat([df, result[0]])
                    optimal_cost = min(result[1], optimal_cost)
        return optimal_cost, df

    def test_set_of_vars(self, vars_w_link_to_id, cost_function, position_in_dfs, sheet_name):
        """ computes the cost function on the testing (or validation) data to assess the identification success

        Parameters
        ----------
        vars_w_link_to_id : list[lib.tom_model.model_elements.variables.fst_dynamics_variables.FastDynamicsVariable]
            the list of variables that have linkages to identify
        cost_function : function
        position_in_dfs : int
            position of the df in self.dfs_optimal_sets (which contains the dfs corresponding to all identification
            processes in the current programme run)
        sheet_name : str

        Returns
        -------

        """
        test_costs = self.get_test_costs_for_best_parameters(vars_w_link_to_id, cost_function, position_in_dfs)
        self.save_test_costs_of_best_sets_of_parameters(position_in_dfs, test_costs, sheet_name)
        return test_costs

    def get_number_of_runs(self, n_parameters):
        """ returns the number of independent runs that should be performed for a group of variables

        Parameters
        ----------
        n_parameters : int
        """
        pass

    def identify(self):
        """ method that calls and manages the identification of the parameters (training phase)

        """
        pass

    def test(self):
        """ method that calls and manages the assessment of the identification process (testing phase)

        """
        pass
    
    # ******************************************************************************************************************
    #                                               Testing
    # ******************************************************************************************************************
    def get_test_costs_for_best_parameters(self, vars_w_link_to_id, cost_function, position_in_dfs):
        """ computes the value of the cost function evaluated with the parameters considered the best training
        (i.e., the parameters that performed the best in the training phase)

        Parameters
        ----------
        vars_w_link_to_id : list[lib.tom_model.model_elements.variables.fst_dynamics_variables.FastDynamicsVariable]
            the list of variables that have linkages to identify
        cost_function : function
        position_in_dfs : int
            position of the df in self.dfs_optimal_sets (which contains the dfs corresponding to all identification
            processes in the current programme run)

        Returns
        -------

        """
        costs = []
        parameters = self.parameters_manager.initialize_parameters(vars_w_link_to_id, self.settings)
        dfs_optimal_sets = self.dfs_optimal_sets[position_in_dfs]
        for i in range(len(dfs_optimal_sets)):      # iterate through dataframe
            j = 0
            for column in list(dfs_optimal_sets.columns):
                if 'param' in column.lower():
                    parameters[j].value = dfs_optimal_sets[column].iloc[i]
                    j += 1
            costs.append(cost_function(parameters))
        return costs

    def save_test_costs_of_best_sets_of_parameters(self, position_in_dfs, test_costs, sheet_name):
        """ saves the test costs obtained with the best sets of parameters to the excel file

        Parameters
        ----------
        position_in_dfs : int
            position of the df in self.dfs_optimal_sets (which contains the dfs corresponding to all identification
            processes in the current programme run)
        test_costs : list[float]
            the testing costs obtained with each set of the best parameters
        sheet_name : str
            name of the sheet in the Excel where the results are saved
        """
        df_w_everything = self.dfs_everything[position_in_dfs]
        df_w_everything.insert(1, 'Test cost',
                               ['', ''] + test_costs + [''] * (len(df_w_everything) - len(test_costs) - 2))
        excel_files.save_df_to_excel_sheet(self.writer, df_w_everything, sheet_name)

    # ******************************************************************************************************************
    #                                       Manage information
    # ******************************************************************************************************************
    def set_train_and_test_data(self):
        """ distributes the data points between train and testing data

        """
        time_steps = set_values_cog.set_values_of_vars_for_cognitive_module(self.tom_model, self.readers,
                                                                            self.n_puzzles, self.hidden_vars,
                                                                            self.overall_id_config.simple_dynamics,
                                                                            self.overall_id_config.normalise_rld_mid_steps)
        if self.overall_id_config.online_data_sets_division:
            if self.overall_id_config.training_set == train_test_config.TrainingSets.B:  # make A and B sets different
                self.random.random()                                                     # but reproducible
            if self.overall_id_config.training_set == train_test_config.TrainingSets.C:  # make A and B sets different
                self.random.random(), self.random.random(), self.random.random()         # but reproducible
            settings_pick_data = pick_train_data.get_settings(self.overall_id_config.simple_dynamics, self.n_horizon)
            self.train_steps, self.test_steps, t_steps_aggregated \
                = pick_train_data.select_train_valid_data(time_steps, settings_pick_data, self.random)
        else:   # get data from predefined set - only for prelim analysis
            self.train_steps, self.test_steps = train_test_config.get_train_valid_steps(self.overall_id_config.training_set)
        print('Train steps:', self.train_steps, '\nTest steps:', self.test_steps)
        self.save_train_and_testing_steps_2_excel()

    def post_process_id_and_test(self):
        """ post process of the entire training and testing process in order to organize and output the results

        """
        self.get_list_of_parameters_4_excel()
        excel_data_processing.write_list_of_parameters_2_excel(self.writer, self.df_params_list)
        overall_performance_df = self.prepare_overall_performance_data()
        excel_files.save_df_to_excel_sheet(self.writer, overall_performance_df, 'Overall Performance')

    def pre_process_identification(self, vars_w_link_to_id):
        """ prepares the data and variables for the identification process

        Parameters
        ----------
        vars_w_link_to_id : list[lib.tom_model.model_elements.variables.fst_dynamics_variables.FastDynamicsVariable]
            the list of variables that have linkages to identify

        Returns
        -------

        """
        parameters = self.parameters_manager.initialize_parameters(vars_w_link_to_id, self.settings)
        n_parameters = len(parameters)
        df = pd.DataFrame(columns=self.get_columns_of_df_w_iterations_results(n_parameters))
        n_runs = self.get_number_of_runs(n_parameters)
        optimal_cost = 1e10
        print('\t\tNumber of runs: ', n_runs, '')
        return parameters, n_parameters, n_runs, df, optimal_cost

    def output_overall_information_of_identification(self, vars_w_link_to_id, df_w_all_runs, parameters_list,
                                                     sheet_name):
        """ outputs the results and the data that came out of the identification process

        Parameters
        ----------
        vars_w_link_to_id : list[lib.tom_model.model_elements.variables.fst_dynamics_variables.FastDynamicsVariable]
            the list of variables that have linkages to identify
        df_w_all_runs :
            df with all the runs of the current identification process
        parameters_list :
            list of all parameters that were identified
        sheet_name :
            name of the sheet where the results will be saved on the Excel writer file
        """
        final_costs, indices_opt_costs, identified_params, df_optimal_sets, df_everything \
            = data.process_final_data_from_identification(df_w_all_runs, parameters_list)
        data.print_overall_id_info(final_costs, indices_opt_costs, identified_params, parameters_list, df_everything,
                                   self.verbose)
        excel_files.save_df_to_excel_sheet(self.writer, df_everything, sheet_name)
        self.dfs_optimal_sets.append(df_optimal_sets)
        self.dfs_everything.append(df_everything)
        self.parameters_manager.get_information_of_parameters(vars_w_link_to_id, self.df_params_list)

    def prepare_1_overall_performance_data(self, overall_data, df_everything_number):
        """ organizes the high level results of 1 identification process and prepares them to be saved for the
        Excel file

        Parameters
        ----------
        overall_data : list[list[float]]
            list with the overall high level results of 1 identification process. The first dimension of the list
            corresponds to the results of one set of parameter, and the second dimension (columns) corresponds to the
            training and testing costs (raw and normalized with different metrics)
        df_everything_number : int
            number of the dataframe in the general list of dataframes self.dfs_everything

        Returns
        -------

        """
        test_costs = self.dfs_everything[df_everything_number].reset_index()['Test cost']
        for i in range(test_costs.shape[0]):
            if isinstance(test_costs[i], str):
                test_costs = test_costs.drop(index=i)
        min_test_cost_idx = test_costs[test_costs == test_costs.min()].index[0]

        ided_params, n_params = self.get_number_of_identified_parameters(df_everything_number)
        for row in [2, min_test_cost_idx]:      # best train cost, best test cost
            t_cost = self.dfs_everything[df_everything_number].iloc[row]['Final cost']
            v_cost = self.dfs_everything[df_everything_number].iloc[row]['Test cost']
            overall_data.append([t_cost, v_cost, t_cost / len(self.train_steps), v_cost / len(self.test_steps),
                                 t_cost / len(self.state_vars), v_cost / len(self.state_vars), ided_params, n_params])
        return overall_data

    def get_number_of_identified_parameters(self, df_everything_number):
        """ computes and returns the number of identified parameters

        Parameters
        ----------
        df_everything_number : int
            number of the dataframe in the general list of dataframes self.dfs_everything


        Returns
        -------

        """
        identified_params, n_params = 0, 0
        df_everything = self.dfs_everything[df_everything_number]
        for column in df_everything.columns:
            if 'Param' in column:
                identified_params += 1 if df_everything.iloc[1][column] else 0
                n_params += 1
        return identified_params, n_params

    def get_columns_of_df_w_iterations_results(self, number_of_parameters):
        """ returns the names of the columns for the dataframe that will contain the detailed information of the
        one identification process

        Parameters
        ----------
        number_of_parameters : int
            number of parameters identified/to be identified

        Returns
        -------

        """
        return ['Final cost'] + ['Param ' + str(i) for i in range(number_of_parameters)] + \
               ['Cost ' + str(i) for i in range(self.settings.n_iterations)]

    def prepare_overall_performance_data(self):
        """ organizes the overall high-level results of the identification process and prepares them to be saved for the
        Excel file

        """
        pass

    def save_train_and_testing_steps_2_excel(self):
        """ saves in the Excel file which datapoints are used for train and which ones are used for testing

        """
        df = pd.DataFrame([[self.train_steps, self.test_steps]], columns=('Train Steps', 'Test steps'))
        excel_files.save_df_to_excel_sheet(self.writer, df, 'Train test steps')

    def get_list_of_parameters_4_excel(self):
        """ returns the list of the parameters identified in one identification process

        """
        params_values, ided_params = list(), list()
        for df in self.dfs_everything:
            for i in range(len(self.df_params_list)):
                try:
                    params_values.append(df.iloc[2]['Param ' + str(i)])
                    ided_params.append(df.iloc[1]['Param ' + str(i)])
                except KeyError:    # when it reads all the parameters of the current df, moves on to next
                    break
        self.df_params_list.insert(len(self.df_params_list.columns), "Values", params_values, True)
        self.df_params_list.insert(len(self.df_params_list.columns), "IDed", ided_params, True)


def one_run_of_gd_multi(run, n_runs, vars_w_link_to_id, optimal_cost, cost_function, df, settings, verbose, tom_model,
                        random, include_cognitive, include_perception, include_slow_dyn,
                        warm_start_perception_params, warm_start_cognition_parameters):
    """ runs one gradient descent identification procedure for a multiprocessing configuration (only one procedure that
    is being run in this function, but it is done in parallel with other similar procedures, using the same function).
    This is the function that can be run multiple times at the same time using multiple processes.

    Parameters
    ----------
    run : int
        number of the current run
    n_runs : int
        total number of runs
    vars_w_link_to_id : list[lib.tom_model.model_elements.variables.fst_dynamics_variables.FastDynamicsVariable]
        the list of variables of to identify
    optimal_cost : float
        current optimal cost
    cost_function : function
        the cost function that determines how close the model with the identified parameters fits the (train or
        test) data
    df : pandas.DataFrame
    settings : Settings
    verbose : int
    tom_model : experimentNao.declare_model.declare_entire_model.ToMModelChessSimpleDyn
        theory of mind model of the participant
    random : random.Random
        the random variable (for traceability)
    include_cognitive : bool
        whether the parameters of the cognitive model are to be identified
    include_perception : bool
        whether the parameters of the perception model are to be identified
    include_slow_dyn : bool
        whether the slow dynamics variables are to be identified
    warm_start_perception_params : Union[list[float], None]
        whether the parameters of the perception model should be warm-started
    warm_start_cognition_parameters : Union[list[float], None]
        whether the parameters of the cognitive model should be warm-started

    Returns
    -------

    """
    id_engine = CognitiveIDEngine(settings, verbose)
    parameters_manager = pm.ParametersManager(tom_model, random, include_slow_dyn,
                                              include_cognitive=include_cognitive, include_perception=include_perception)
    optimal_cost = id_engine.run_one_gd(run, n_runs, vars_w_link_to_id, optimal_cost, cost_function, df, parameters_manager,
                                        warm_start_perception_params, warm_start_cognition_parameters)
    return df, optimal_cost


class CognitiveIDEngine:
    def __init__(self, settings, verbose):
        """ Takes care of 1 identification process. This class makes the bridge between the CognitiveIdentification,
        which manages all the data related to the identification of the ToM model and the high-level identification,
        and the library class that can be used to identify anything using gradient descent.

        Parameters
        ----------
        settings : lib.algorithms.gradient_descent.settings.Settings
        verbose : int
        """
        self.settings = settings
        self.verbose = verbose

    def run_one_gd(self, run, n_runs, vars_w_link_to_id, optimal_cost, cost_function, df, parameters_manager,
                   warm_start_perception_parameters=None, warm_start_cognition_parameters=None):
        """ runs one procedure of gradient descent

        Parameters
        ----------
        run : int
            number of the current run
        n_runs : int
            total number of runs
        vars_w_link_to_id : list[lib.tom_model.model_elements.variables.fst_dynamics_variables.FastDynamicsVariable]
            the list of variables of to identify
        optimal_cost : float
            current optimal cost
        cost_function : function
            the cost function that determines how close the model with the identified parameters fits the (train or
            test) data
        df : pandas.DataFrame
        parameters_manager : pm.ParametersManager
            object that manages the parameters to be identified
        warm_start_perception_parameters : Union[list[float], None]
            whether the parameters of the perception model should be warm-started
        warm_start_cognition_parameters : Union[list[float], None]
            whether the parameters of the cognitive model should be warm-started

        Returns
        -------

        """
        st, parameters_2_id = self.pre_process_gd_run(vars_w_link_to_id, optimal_cost, parameters_manager)
        if warm_start_perception_parameters is not None:
            self.set_warm_start_perception(parameters_2_id, warm_start_perception_parameters)
        if warm_start_cognition_parameters is not None:
            self.set_warm_start_cognition(parameters_2_id, warm_start_cognition_parameters)
        if self.settings.verbose >= 1:
            print('\n\n\nParameters: ', [warm_start_perception_parameters], '\n',
                  [par.value for par in parameters_2_id])
        param, costs = gd.run_gradient_descent(self.settings, parameters_2_id, cost_function)
        df, optimal_cost = self.post_process_gd_run(run, costs, param, st, n_runs, df, optimal_cost)
        return optimal_cost

    def pre_process_gd_run(self, vars_w_link_to_id, optimal_cost, parameters_manager):
        """ runs necessary steps before 1 gradient descent procedure

        Parameters
        ----------
        vars_w_link_to_id : list[lib.tom_model.model_elements.variables.fst_dynamics_variables.FastDynamicsVariable]
            the list of variables of to identify
        optimal_cost : float
            current optimal cost
        parameters_manager : pm.ParametersManager
            object that manages the parameters to be identified

        Returns
        -------

        """
        st = time.time()
        self.settings.set_cost_required_half_time(optimal_cost)
        parameters_2_id = parameters_manager.initialize_parameters(vars_w_link_to_id, self.settings)
        return st, parameters_2_id

    def post_process_gd_run(self, run, costs, parameters, starting_time, n_runs, df, overall_optimal_cost):
        """ runs necessary steps after 1 gradient descent procedure

        Parameters
        ----------
        run : int
            number of the current run
        costs : List[numpy.float64]
            list of the costs obtained in each iteration of the gradient descent process
        parameters : List[numpy.float64]
        starting_time : float
        n_runs : int
        df : pandas.core.frame.DataFrame
        overall_optimal_cost : float

        Returns
        -------

        """
        data.print_info_of_1_run(run, costs, parameters, starting_time, n_runs, self.verbose)
        best_cost_of_this_run = costs[-1]
        overall_optimal_cost = min(overall_optimal_cost, costs[-1])     # update optimal overall (of all runs) cost
        if len(costs) < self.settings.n_iterations:         # add "None" for the iterations with no cost (after pruning)
            costs.extend([None] * (self.settings.n_iterations - len(costs)))
        df.loc[len(df.index)] = [best_cost_of_this_run] + [round(ele, 3) for ele in parameters] + costs
        return df, overall_optimal_cost

    def set_warm_start_perception(self, parameters_2_id, warm_start_perception_parameters):
        """ sets the initial values of the parameters of the perception module using the given values

        Parameters
        ----------
        parameters_2_id : list[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]
            parameters to be identified in this gradient descent procedure
        warm_start_perception_parameters : Union[list[float], None]
            whether the parameters of the perception model should be warm-started
        """
        # the m parameters of 'warm_start_perception_parameters' are the last m parameters of 'parameters_2_id'
        n_params_cog = len(parameters_2_id) - len(warm_start_perception_parameters)
        for i in range(len(warm_start_perception_parameters)):
            parameters_2_id[n_params_cog + i].value = warm_start_perception_parameters[i]

    def set_warm_start_cognition(self, parameters_2_id, warm_start_cognition_parameters):
        """ sets the initial values of the parameters of the cognitive module using the given values

        Parameters
        ----------
        parameters_2_id : list
            parameters to be identified in this gradient descent procedure
        warm_start_cognition_parameters : Union[list[float], None]
            whether the parameters of the cognitive model should be warm-started
        """
        for i in range(len(warm_start_cognition_parameters)):
            parameters_2_id[i].value = warm_start_cognition_parameters[i]