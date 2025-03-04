import pandas as pd

from experimentNao import participant
from experimentNao.data_analysis.post_id_analysis import files_of_comparison
from experimentNao.data_analysis.post_id_analysis import paths_and_files
from experimentNao.model_ID.configs import overall_config
from experimentNao.model_ID.configs.train_test_config import TrainingSets
from lib import excel_files


class ResultsDf:
    def __init__(self):
        self.train = pd.DataFrame()
        self.test = pd.DataFrame()

    def add_empty_line(self, train=True, test=True):
        if train:
            self.train = excel_files.add_empty_line_to_df(self.train)
        if test:
            self.test = excel_files.add_empty_line_to_df(self.test)

    def add_row_to_results(self, new_row_train=None, new_row_test=None):
        if new_row_train is not None:
            self.train = pd.concat([self.train, new_row_train])
        if new_row_test is not None:
            self.test = pd.concat([self.test, new_row_test])


def process_one_id(general_path_, id_config_, dfs_all_performances_, dfs_individual_costs_):
    try:
        df_performance_t, df_performance_v, df_individual_costs_t, df_individual_costs_v, df_params \
            = paths_and_files.get_dfs_from_file(general_path_, id_config_)
        # Remove the cost / data points columns
        # n_train_points = round(df_performance_t.loc[0, 'Train Cost']/df_performance_t.loc[0, 'Train cost / steps'])
        # n_test_points = round(df_performance_t.loc[0, 'Test Cost']/df_performance_t.loc[0, 'Test Cost / steps'])
        df_performance_t = df_performance_t.drop(columns=['Train cost / steps', 'Test Cost / steps'])
        df_performance_v = df_performance_v.drop(columns=['Train cost / steps', 'Test Cost / steps'])
        # Add name to each new row - corresponding to one IDed model
        for df in [df_performance_t, df_performance_v, df_individual_costs_t, df_individual_costs_v]:
            df.at[0, df.columns[0]] = file_name.replace('model_id_' + participant_id + '_', '')
        for df in [df_performance_t, df_performance_v]:
            df['% params'] = df['IDed Params'][0] / df['N params'][0]  # % of params that were identified
            # df.insert(5, 'T cost / (steps * vars)', df['Train cost / vars'] / n_train_points)
            # df.insert(6, 'V cost / (steps * vars)', df['Test Cost / vars'] / n_test_points)
        # Rename columns
        names_change = {'Test Cost': 'Valid Cost',
                        'Train cost / vars': 'T cost/vars', 'Test Cost / vars': 'V cost/vars'}
        df_performance_t = df_performance_t.rename(columns=names_change)
        df_performance_v = df_performance_v.rename(columns=names_change)
        df_performance_t = df_performance_t.round(4)
        # Concat info from file to df with all files
        dfs_all_performances_.add_row_to_results(new_row_train=df_performance_t,
                                                 new_row_test=df_performance_v)
        dfs_individual_costs_.add_row_to_results(new_row_train=df_individual_costs_t,
                                                 new_row_test=df_individual_costs_v)
    except FileNotFoundError:
        print('NOT READ FILE: ', file_name)


# ***********************************************  Process ******************************************************
participant_id = participant.participant_identifier
comparison_round = 4
comparisons = ['prelim_official',                 # 0
               'simple_model',                    # 1 <- set best sep_per
               'special_incr', 'extra_simple',    # 2 3 <- set best sep_per
               'cost_n']                          # 4 <- set best config
current_folder, model_configs, id_modes,  simple_dyns, incrementals, n_horizons, normalise_rld_options \
    = files_of_comparison.get_comparison_configs(comparisons[comparison_round],
                                                 *files_of_comparison.get_best_sep_per_of_participant(participant_id))

dfs_all_performances, dfs_individual_costs = ResultsDf(), ResultsDf()
dfs_all_performances.add_empty_line()
dfs_all_individuals = pd.DataFrame()
general_path = paths_and_files.get_folder_path_new(current_folder, participant_id)
for train_set in [TrainingSets.A, TrainingSets.B]:
    for config in model_configs:
        for id_mode in id_modes:
            for simple_dyn in simple_dyns:
                for incr in incrementals:
                    for n_horizon in n_horizons:
                        for normalise_rld_mid_steps in normalise_rld_options:
                            id_config = overall_config.IDConfig(config, participant_id, id_mode, train_set, simple_dyn,
                                                                incremental=incr, n_horizon=n_horizon, cog_2_id=True,
                                                                normalise_rld_mid_steps=normalise_rld_mid_steps)
                            file_name = id_config.get_model_id_file_name()
                            process_one_id(general_path, id_config, dfs_all_performances, dfs_individual_costs)
    dfs_all_performances.add_empty_line()
    dfs_individual_costs.add_empty_line()
    dfs_all_individuals = pd.concat([dfs_all_individuals, dfs_individual_costs.train, dfs_individual_costs.test])
    dfs_individual_costs = ResultsDf()

# Format DFs of performances
df_all_performances_train = dfs_all_performances.train.reset_index(drop=True)
df_all_performances_test = dfs_all_performances.test.reset_index(drop=True)
df_all_performances_train.at[0, df_all_performances_train.columns[0]] = 'Best train'
df_all_performances_test.at[0, df_all_performances_test.columns[0]] = 'Best test'
dfs_all_performances = pd.concat([df_all_performances_train, df_all_performances_test])

paths_and_files.write_comparison_excel_file(general_path, comparison_round, comparisons[comparison_round],
                                            dfs_all_performances, dfs_all_individuals, participant_id)
print('Finished')
