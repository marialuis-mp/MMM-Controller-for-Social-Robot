import pandas as pd

from experimentNao.model_ID.cognitive import identification_cognitive as id_
from experimentNao.model_ID.cognitive.cost_management import Cost
from lib import excel_files


# ######################################################################################################################
#
#                          To ID all the parameters of the cognitive module at once
#
# ######################################################################################################################


class CognitiveIdAll(id_.CognitiveIdentification):
    def __init__(self, tom_model, n_puzzles, writer_files, reader_files, prune, included_vars, random,
                 overall_id_config, short_mode=False, verbose=0, delft_blue=False):
        """ identification system that identifies all the variables of the cognitive model at once. See parent class
        for description of parameters.

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
        """
        super().__init__(tom_model, n_puzzles, writer_files, reader_files, prune, random, overall_id_config, short_mode,
                         verbose, delft_blue=delft_blue)
        self.id_mode = self.overall_id_config.id_cog_mode
        # Settings groups of vars
        self.state_vars = self.tom_model.cognitive_module.state_vars
        self.aux_vars = self.tom_model.cognitive_module.aux_vars
        self.vars_2_id, self.hidden_vars = self.tom_model.cognitive_module.get_vars_2_id_and_hidden_vars(included_vars)
        self.vars_w_linkages_to_id \
            = self.tom_model.cognitive_module.get_vars_w_link_to_id(self.vars_2_id,
                                                                    self.overall_id_config.simple_dynamics)
        # Costs and data saving
        self.cost = Cost(self.state_vars, self.vars_2_id, self.vars_w_linkages_to_id, tom_model, self.n_horizon,
                         overall_id_config.simple_dynamics)
        self.overall_df_number = 0

    def identify(self, sheet_name='ID'):
        if not self.with_multiprocess:
            cost, parameters_manager = self.cost, self.parameters_manager
        else:
            cost = Cost(self.state_vars, self.vars_2_id, self.vars_w_linkages_to_id, self.tom_model, self.n_horizon,
                        self.overall_id_config.simple_dynamics)
        the_cost_function = lambda params, ts=self.train_steps, pm=self.parameters_manager: cost.cost_function(params, ts, pm)
        self.identify_set_of_variables(self.vars_w_linkages_to_id, cost_function=the_cost_function, sheet_name=sheet_name)

    # ******************************************************************************************************************
    #                                               Cost function
    # ******************************************************************************************************************

    def test(self, position_in_dfs=0, sheet_name='ID'):
        ttl_costs_train = self.get_test_costs_for_best_parameters(self.vars_w_linkages_to_id,
                                                                  lambda p, s=self.train_steps,
                                                                         pm=self.parameters_manager:
                                                                  self.cost.cost_function(p, s, pm), position_in_dfs)
        ttl_costs_test = self.test_set_of_vars(self.vars_w_linkages_to_id,
                                               lambda p, s=self.test_steps, pm=self.parameters_manager:
                                               self.cost.cost_function(p, s, pm), position_in_dfs, sheet_name=sheet_name)
        individual_costs = []
        for steps in [self.train_steps, self.test_steps]:
            individual_costs.append(
                self.get_test_costs_for_best_parameters(self.vars_w_linkages_to_id,
                                                        lambda par, s=steps: self.cost_function_separate_by_var(par, s),
                                                        position_in_dfs))
        self.save_costs_by_var(individual_costs[0], individual_costs[1], ttl_costs_train, ttl_costs_test)
        return ttl_costs_test

    # ******************************************************************************************************************
    #                                               Testing
    # ******************************************************************************************************************
    def cost_function_separate_by_var(self, parameters_2_id, training_steps):
        """ Computes the cost function, but for each variable independently. It is useful to see the contribution of
        each variable to the total cost.

        Parameters
        ----------
        parameters_2_id : list[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]
        training_steps : list[int]

        Returns
        -------

        """
        costs = [0] * len(self.vars_2_id)
        for i in range(len(self.vars_2_id)):
            costs[i] = self.cost.cost_function(parameters_2_id, training_steps, self.parameters_manager, [self.vars_2_id[i]])
        return costs

    def save_costs_by_var(self, individual_costs_train, individual_costs_test, total_costs_train, total_costs_test):
        """ saves the individual cost of each variable

        Parameters
        ----------
        individual_costs_train : list[float]
        individual_costs_test : list[float]
        total_costs_train : list[float]
        total_costs_test : list[float]
        """
        columns = ['Total train cost'] + ['Total test cost'] + ['Cost ' + var.name for var in self.vars_2_id]
        df = pd.DataFrame(columns=columns)
        assert len(individual_costs_train) == len(individual_costs_test)
        for i in range(len(individual_costs_test)):
            df = pd.concat(
                [df, pd.DataFrame([[total_costs_train[i], ''] + individual_costs_train[i]], columns=columns)])
            df = pd.concat([df, pd.DataFrame([['', total_costs_test[i]] + individual_costs_test[i]], columns=columns)])
        excel_files.save_df_to_excel_sheet(self.writer, df, 'Individual costs')

    # ******************************************************************************************************************
    #                                               Data process
    # ******************************************************************************************************************
    def prepare_overall_performance_data(self):
        columns = ('Train Cost', 'Test Cost', 'Train cost / steps', 'Test Cost / steps',
                   'Train cost / vars', 'Test Cost / vars', 'IDed Params', 'N params')
        data = []
        self.prepare_1_overall_performance_data(data, df_everything_number=self.overall_df_number)
        overall_performance_df = pd.DataFrame(data, columns=columns)
        return overall_performance_df

    def get_number_of_runs(self, n_parameters):
        return self.settings.default_n_runs
