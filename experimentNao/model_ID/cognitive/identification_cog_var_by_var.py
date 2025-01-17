import pandas as pd

from lib.tom_model.model_elements.variables.fst_dynamics_variables import Belief
from experimentNao.model_ID.cognitive import identification_cognitive as id_, perception_beliefs_ID as percept_ID


# ######################################################################################################################
#
#
#                    To ID the parameters of each variable of the cognitive module separately
#
# ######################################################################################################################
class CognitiveId1by1(id_.CognitiveIdentification):
    def __init__(self, tom_model, n_puzzles, writer_files, reader_files, prune, random, overall_id_config,
                 short_mode=False, verbose=0, id_beliefs=True, id_goals=True, id_emotions=True):
        """ identification system that identifies the variables of the cognitive model one by one. See parent class
        for description of parameters. This was not used in the experiment.

        Parameters
        ----------
        tom_model : experimentNao.declare_model.declare_entire_model.ToMModelChessSimpleDyn
        n_puzzles : List[int]
        writer_files : pandas.io.excel._openpyxl.OpenpyxlWriter
        reader_files : List[pandas.io.excel._base.ExcelFile]
        prune : bool
        random : random.Random
        overall_id_config : experimentNao.model_ID.configs.overall_config.IDConfig
        short_mode : bool
        verbose : int
        id_beliefs : bool
        id_goals : bool
        id_emotions : bool
        """
        super().__init__(tom_model, n_puzzles, writer_files, reader_files, prune, random, overall_id_config, short_mode,
                         verbose)
        self.id_beliefs = id_beliefs
        self.id_goals = id_goals
        self.id_emotions = id_emotions

    def identify(self):
        self.set_vars_2_id()
        for var in self.state_vars:
            print('\n****** Variable: ', var.name, ' ******')
            self.identify_set_of_variables([var],
                                           lambda params, v=var, ts=self.train_steps: self.cost_function(v, params, ts),
                                           'ID ' + var.name.replace('/', '-'))

    def test(self):
        for i in range(len(self.state_vars)):
            var = self.state_vars[i]     # each df of list 'dfs_best_parameters' corresponds to a var
            self.test_set_of_vars([var], lambda par, v=var, ts=self.test_steps: self.cost_function(v, par, ts),
                                  position_in_dfs=i, sheet_name='ID ' + var.name.replace('/', '-'))

    def cost_function(self, variable, parameters2optimise, train_steps):
        """ cost function for the identification process. This function computes a cost that reflects how incorrect
        the predictions done by the model are with respect to the ground truth (train or test data), depending on the
        current parameters

        Parameters
        ----------
        variable :
        parameters2optimise :
        train_steps :

        Returns
        -------

        """
        self.parameters_manager.set_values_of_parameters(parameters2optimise, [variable])
        cost = 0
        for i in train_steps:       # for each time step
            if isinstance(variable, Belief):  # if beliefs --> the influencer values come from the modules module
                percept_ID.pre_process_belief_influencer(variable, self.tom_model.perception_module, i-1)
            else:                           # if goal or emotion --> the influencers values must be set (simple process)
                for inf in variable.influencers:
                    inf.influencer_variable.value = inf.influencer_variable.values[i-1]
                    if inf.has_side_linkage:
                        inf.side_linkage.value = inf.side_linkage.values[i-1]
            variable.compute_variable_value_fcm()
            cost_of_episode = (variable.next_value - variable.values[i]) ** 2
            cost += cost_of_episode
        return cost

    def set_vars_2_id(self):
        """ sets the variables that will be identified

        """
        self.state_vars = tuple()
        if self.id_beliefs:
            self.state_vars = self.state_vars + self.tom_model.cognitive_module.get_beliefs()
        if self.id_goals:
            self.state_vars = self.state_vars + self.tom_model.cognitive_module.get_goals()
        if self.id_emotions:
            self.state_vars = self.state_vars + self.tom_model.cognitive_module.get_emotions()

    def get_number_of_runs(self, n_parameters):
        return min(max(self.settings.min_n_runs, n_parameters ** 3), self.settings.max_n_runs)

    def prepare_overall_performance_data(self):
        columns = ('Parameter name', 'Train Cost', 'Valid Cost', 'Train cost N params', 'Valid Cost N params',
                   'Train cost N vars', 'Valid Cost N vars', 'IDed Params')
        data = []
        for i in range(len(self.dfs_everything)):
            data = self.prepare_1_overall_performance_data(data, df_everything_number=i)
            data[-1] = [self.state_vars[i].name] + data[-1]
        overall_performance_df = pd.DataFrame(data, columns=columns)
        return overall_performance_df
