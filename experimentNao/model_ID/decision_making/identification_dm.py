from enum import Enum
import time
import pandas as pd

from experimentNao.model_ID.decision_making.parameters_manager import ParametersManagerDM
from lib import excel_files
from lib.algorithms.gradient_descent import settings as gd_set, gradient_descent_opt as gd
from lib.algorithms.genetic_algorithm import settings as ga_set, genetic_algorithm_opt as ga
from lib.algorithms.genetic_algorithm.select_parents_for_operatorions import ParentSelection
from experimentNao.model_ID.data_processing import pick_train_data
from experimentNao.model_ID.data_processing import optimisation_data_processing as data


class OptMode(Enum):
    GRADIENT_DESCENT = 1
    GENETIC_ALGORITHM = 2


class DMIdentification:
    def __init__(self, dm_module, n_puzzles, train_data_settings, train_mode, random, writer_files, reader_files,
                 boundary_values=(-1, 1)):
        """ identification system that identifies all the parameters of the decision-making at once.


        Parameters
        ----------
        dm_module :
        n_puzzles :
        train_data_settings :
        train_mode :
        random :
        writer_files :
        reader_files :
        boundary_values :
        """
        self.dm_module = dm_module                              # module
        self.train_data_settings = train_data_settings
        self.train_mode = train_mode
        self.n_puzzles = n_puzzles
        self.boundary_values = boundary_values  # minimum and maximum values of parameters
        self.writer, self.reader = writer_files, reader_files   # excel files
        self.parameters_list = None             # list w/ all the objects of class 'Parameter2Optimise'
        self.optimal_parameters_values = None   # list w/ the values of best sets of params (order of 'parameters_list')
        self.optimal_train_cost = None          # optimal (minimal) cost obtained during the training process
        self.settings = None
        self.df_best_parameters = pd.DataFrame(columns=['Name of parameter', 'ID Value', 'Value'])
        self.set_settings()
        self.random = random
        self.parameters_manager = ParametersManagerDM(self.settings, boundary_values, self.random)

    def set_settings(self):
        """ defines the settings and hyperparameters for the identification

        """
        if self.train_mode == OptMode.GRADIENT_DESCENT:
            self.settings = gd_set.Settings(n_iterations=int(1e1), min_number_of_runs=200, max_number_of_runs=200,
                                            initial_learning_rate=0.1, changing_learning_rate=False,
                                            differentiation_step=0.1, max_differentiation_step=0.8,
                                            boundary_values=self.boundary_values, verbose=0, multiprocess=False,
                                            compute_cost_at_end_of_iteration=True, write_to_excel=False)
        elif self.train_mode == OptMode.GENETIC_ALGORITHM:
            self.settings = ga_set.Settings(n_iterations=int(1e1), n_solutions=int(5e3), verbose=0, mutation_range=1.0,
                                            percentage_crossover=0.25, percentage_mutation=0.25,
                                            arithmetic_crossover_weight=0.6, n_solutions_in_tournament=4,
                                            parent_selection_method=ParentSelection.TOURNAMENT)

    # **********************************************************************************************************************
    #                                           identification
    # **********************************************************************************************************************
    def identify_dm(self, train_steps, intentions):
        """ method that calls and manages the identification of the parameters (training phase) of the decision-making
        module

        Parameters
        ----------
        train_steps : List[int]
        intentions : List[experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame]
        """
        if self.train_mode == OptMode.GRADIENT_DESCENT:
            self.identify_dm_gd(train_steps, intentions)
        elif self.train_mode == OptMode.GENETIC_ALGORITHM:
            self.identify_dm_ga(train_steps, intentions)

    def identify_dm_gd(self, train_steps, intentions):
        """ method that calls and manages the identification of the parameters (training phase) of the decision-making
        module using gradient descent

        Parameters
        ----------
        train_steps : List[int]
        intentions : List[experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame]
        """
        n_params, n_runs = self.parameters_manager.get_n_params_and_runs(intentions)
        self.optimal_train_cost, self.optimal_parameters_values = 1e4, list()  # are optimised together
        for i in range(n_runs):  # \-> with many parameters -> need more runs
            st = time.time()
            self.parameters_list = self.parameters_manager.initialize_parameters(intentions)
            params, costs = gd.run_gradient_descent(self.settings, self.parameters_list,
                                                    lambda parameters, ts=train_steps, ints=intentions:
                                                    self.cost_function(parameters, ts, ints))
            data.print_info_of_1_run(i, costs, params, st, n_runs, self.settings.verbose)
            self.save_minimum_cost(costs[-1], params)

    def identify_dm_ga(self, train_steps, intentions):
        """ method that calls and manages the identification of the parameters (training phase) of the decision-making
        module using a genetic algorithm

        Parameters
        ----------
        train_steps : List[int]
        intentions : List[experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame]
        """
        self.parameters_list = self.parameters_manager.initialize_parameters(intentions)
        solutions = ga.run_ga(self.parameters_list, self.settings,
                              lambda parameters, ts=train_steps, i=intentions: self.cost_function(parameters, ts, i))
        self.optimal_train_cost = 1 / solutions[0].fitness
        self.optimal_parameters_values = [s.parameters for s in solutions if s.fitness == solutions[0].fitness][0:50]

    def cost_function(self, parameters, train_steps, intentions):
        """ cost function for the identification process. This function computes a cost that reflects how incorrect
        the predictions done by the model are with respect to the ground truth (train or test data), depending on the
        current parameters

        Parameters
        ----------
        parameters : List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]
        train_steps : List[int]
        intentions : List[experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame]

        Returns
        -------

        """
        pass

    # **********************************************************************************************************************
    #                                               Data Management
    # **********************************************************************************************************************
    def select_train_and_valid_data(self, time_steps):
        """ divides the data points into train and testing data

        Parameters
        ----------
        time_steps : List[List[float]]

        Returns
        -------

        """
        return pick_train_data.select_train_valid_data(time_steps, self.train_data_settings, self.random)

    @property
    def get_all_intentions(self):
        """ return all the intentions of the dm module

        Returns
        -------

        """
        return self.dm_module.intention_selector.outputs

    def get_all_actions(self):
        """ return all the actions of the dm module

        Returns
        -------

        """
        return self.dm_module.action_selector.outputs

    # **********************************************************************************************************************
    #                                               Output Information
    # **********************************************************************************************************************
    def output_identification_info(self, train_steps, intention=None):
        """ outputs the identification information

        Parameters
        ----------
        train_steps : List[int]
        intention : experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame

        Returns
        -------

        """
        df_all = self.write_id_results_2_excel(train_steps, intention)
        print('*** Train steps ({}): {}'.format(len(train_steps), train_steps),
              '\n\t*** Optimal parameters:', self.optimal_parameters_values if len(self.optimal_parameters_values) <= 5
              else self.optimal_parameters_values[0:5],
              '\n\t*** Optimal cost:', self.optimal_train_cost)
        return df_all

    def output_testing_info(self, df_all, test_costs, test_steps, most_accurate_threshold=None, intentions_group=None):
        """ outputs the information about the testing of the identified module

        Parameters
        ----------
        df_all : pandas.DataFrame
        test_costs : List[float]
        test_steps : List[int]
        most_accurate_threshold : Union[float, None]
        intentions_group : List[experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame]

        Returns
        -------

        """
        df_all.insert(1, 'testing cost', test_costs)
        df_all.insert(3, 'normalized testing cost', [cost / len(test_steps) for cost in test_costs])
        excel_files.save_df_to_excel_sheet(self.writer, df_all, self.get_name_of_excel_sheet(intentions_group[0]))
        print('*** Test steps ({}): {}'.format(len(test_steps), test_steps), '\n\t*** Testing Costs: ', test_costs)
        opt_parameters_df = self.save_best_parameters(df_all, test_costs, most_accurate_threshold)
        return df_all

    def write_id_results_2_excel(self, train_steps, intention=None):
        """ writes the results of the identification process to excel file

        Parameters
        ----------
        train_steps : List[int]
        intention : experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame

        Returns
        -------

        """
        parameters_2_write = []
        for params_group in self.optimal_parameters_values:
            parameters_2_write.append([self.optimal_train_cost, self.optimal_train_cost / len(train_steps)] + params_group)
        df = pd.DataFrame(parameters_2_write,
                          columns=['train cost', 'normalized train cost'] + [par.name for par in self.parameters_list])
        excel_files.save_df_to_excel_sheet(self.writer, df, self.get_name_of_excel_sheet(intention))
        return df

    def get_name_of_excel_sheet(self, intention=None):
        """ returns name of the excel sheet where the output of the identification process regarding the parameters
        associated with "intention" is stored

        Parameters
        ----------
        intention : experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame

        Returns
        -------

        """
        return ('DM' if intention is None else intention.name) + ' ID - ' \
               + ('GA' if self.train_mode == OptMode.GENETIC_ALGORITHM else 'GD')

    def save_best_parameters(self, df_all, test_costs, most_accurate_threshold):
        """ saves the best parameters for the MBC in the dataframe self.df_best_parameters

        Parameters
        ----------
        df_all : pandas.DataFrame
        test_costs : List[float]
        most_accurate_threshold : Union[float, None]
        """
        min_index = test_costs.index(min(test_costs))
        opt_parameters_df = df_all.iloc[min_index]
        data = list()
        j = 0
        for item in opt_parameters_df.items():
            if 'threshold' in item[0]:
                mbc_value = item[1] if most_accurate_threshold[j] is None else most_accurate_threshold[j]
                data.append([item[0], item[1], mbc_value])
                j += 1
        self.df_best_parameters = pd.concat([self.df_best_parameters, pd.DataFrame(data, columns=self.df_best_parameters.columns)])

    # **********************************************************************************************************************
    #                                   Costs
    # **********************************************************************************************************************
    def cost_of_predicting_intention(self, intention, step):
        """ computes a cost that reflects how incorrect the prediction done by the model about an intention is with
        respect to the ground truth

        Parameters
        ----------
        intention : experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame
        step : int

        Returns
        -------

        """
        if intention.active != intention.intentions_sequence[step]:
            return 1
        else:
            return 0

    def save_minimum_cost(self, new_c, new_pars):
        """ saves the minimum cost that was obtained so far in the identification process (this is useful for pruning)

        Parameters
        ----------
        new_c : int
        new_pars :
        """
        if new_c < self.optimal_train_cost:
            self.optimal_train_cost = new_c
            self.optimal_parameters_values = [new_pars]
        elif new_c == self.optimal_train_cost:
            self.optimal_parameters_values.append(new_pars)
