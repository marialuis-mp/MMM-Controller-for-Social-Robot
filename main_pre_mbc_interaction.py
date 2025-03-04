import statistics

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

from lib import excel_files
from experimentNao import participant
from experimentNao.declare_model import declare_entire_model as dem, chess_interaction_data as cid
from experimentNao.model_ID.data_processing import excel_data_processing as edp
from experimentNao.data_analysis.pre_process_data import bulk_processing_of_data as bpd, file_names, \
    get_metrics_from_dfs as get_metrics


def get_rld_names(indices):
    name_list = cid.get_data_titles()
    return [name_list[index] for index in indices]


# ********************************************* Start of main *********************************************
N_difficulties = 6
name_participant = participant.participant_identifier
flatten_rld_metrics_per_diff = True
reader_files, n_puzzles = edp.pre_process_participant_input_files(participant.participant_identifier)
print('{} files, n puzzles per file: {}'.format(len(n_puzzles), n_puzzles))

# A. Sort metrics and belief by REAL difficulty - initial analysis
belief_difficulty_by_diff = [[] for _ in range(N_difficulties)]
rld_names_by_diff = get_rld_names(indices=[0, 1, 4, 8])     # without difficulty
metrics_by_diff = [[[] for _ in range(N_difficulties)] for __ in range(len(rld_names_by_diff))]
metrics_proportion_by_diff = [[] for _ in range(len(rld_names_by_diff))]

# B. Sort metrics by BELIEF difficulty - new analysis
puzzle_difficulty_beliefs = list()
rld_names = get_rld_names(indices=[0, 1, 2, 4, 8])
all_rld_values = [[] for _ in range(len(rld_names))]

vars_names = ('game difficulty', 'confident/frustrated', 'interested/bored', 'quit game', 'change game difficulty',
              'skip puzzle', 'get help')
variables = [[] for _ in range(len(vars_names))]

# Data collection
max_rld_values = dem.get_normalization_values_of_rld(reader_files, from_id=False)
n_data_points_per_session = [0]
for i in range(len(reader_files)):
    performance_df = edp.get_specific_sheets_from_file(reader_files[i], 'Performance', name_cant_contain=[])[0]
    quit_in_last = performance_df['Quit'][len(performance_df)-1]
    if quit_in_last:
        performance_df.drop(performance_df.tail(1).index, inplace=True)
    for puzzle_number in range(n_puzzles[i]-1 if quit_in_last else n_puzzles[i]):
        puzzle_dfs = edp.get_specific_sheets_from_file(reader_files[i], 'Step ' + str(puzzle_number) + '.',
                                                       name_cant_contain=['help'])
        # A. Get metrics of each puzzle and sort them by difficulty
        real_difficulty = get_metrics.get_metric_in_step(performance_df, float(puzzle_number), 'puzzle_difficulty')
        skipped_puzzle = get_metrics.get_metric_in_step(performance_df, float(puzzle_number), 'skipped_puzzle')
        for j in range(len(rld_names_by_diff)):
            value = get_metrics.get_first_metric_in_a_puzzles(performance_df, puzzle_number, rld_names_by_diff[j])
            if skipped_puzzle:
                print('Do not save data point for normalization, puzzle ', puzzle_number, j)
            else:
                metrics_by_diff[j][real_difficulty].append(value)
            last_value = get_metrics.get_final_metric_in_a_puzzles(performance_df, puzzle_number, rld_names_by_diff[j])
            if last_value != 0:
                metrics_proportion_by_diff[j].append(value/last_value if last_value != 0 else last_value)
        # AB. Iterate through the steps that correspond to the puzzle (1, 2 or 3) - get beliefs of each step
        for df in puzzle_dfs:
            belief_difficulty = get_metrics.get_var_value_from_step(df, 'game difficulty')
            if not skipped_puzzle:
                belief_difficulty_by_diff[real_difficulty].append(belief_difficulty)    # A. Sort belief_difficulty by diff
            puzzle_difficulty_beliefs.append(belief_difficulty / 5 - 1)                 # B. Save belief data point
            for jj in range(len(vars_names)):
                variables[jj].append(get_metrics.get_var_value_from_step(df, vars_names[jj]))
    # B. Get all values of RLD
    for j in range(len(all_rld_values)):
        all_rld_values[j].extend(list(performance_df[rld_names[j]]))
    n_data_points_per_session.append(len(variables[0]))

# B. normalize values
for j in range(len(all_rld_values)):
    if rld_names[j] == 'skipped_puzzle':
        all_rld_values[j] = bpd.normalize_vector([1 if ele else -1 for ele in all_rld_values[j]], 1)
    else:
        if rld_names[j] == 'n_wrong_attempts':
            all_rld_values[j] = [bpd.extract_value_of_wrong_attempts(value_wa) for value_wa in all_rld_values[j]]
        all_rld_values[j] = bpd.normalize_vector(all_rld_values[j], max_rld_values[rld_names[j]])

# ************************************ Presenting the model_id_out *****************************************************
print('\n**************** A. Results by difficulty values **************** ')
for i in range(len(belief_difficulty_by_diff)):
    if len(belief_difficulty_by_diff[i]) > 0:
        print('Difficulty: {}'.format(i))
        bpd.print_arrays_and_averages(belief_difficulty_by_diff[i], 'Belief difficulty')
        for j in range(len(metrics_by_diff)):
            bpd.print_arrays_and_averages(metrics_by_diff[j][i], rld_names_by_diff[j])
metrics_by_diff_normalised = bpd.normalise_rld_metrics_per_diff(metrics_by_diff, rld_names_by_diff)

print('\n**************** A2. Proportions of RLD at beginning/end of puzzle **************** ')
for j in range(len(metrics_proportion_by_diff)):
    print('\nTime proportions of {}: {}'.format(rld_names_by_diff[j], metrics_proportion_by_diff[j]),
          '\tOn average: ', sum(metrics_proportion_by_diff[j])/len(metrics_proportion_by_diff[j]) if len(metrics_proportion_by_diff[j])>0 else None)

print('\n**************** B. Results to relate beliefs of difficulty with RLD **************** ')
print('All beliefs: ', puzzle_difficulty_beliefs)
max_decimals = 4
for i in range(len(all_rld_values)):
    X = np.array(all_rld_values[i]).reshape(-1, 1)
    y = np.array(puzzle_difficulty_beliefs)
    reg = LinearRegression().fit(X, y)
    print('\n{}\nCoefficients:  y = {} x + {} \t Score: {}'.format(rld_names[i], round(reg.coef_[0], max_decimals),
                                                                   round(reg.intercept_, max_decimals),
                                                                   round(reg.score(X, y), max_decimals)))

print('\n Results to relate beliefs of difficulty with all RLDs')
X = np.transpose(np.array(all_rld_values))
y = np.array(puzzle_difficulty_beliefs)
# reg = LinearRegression().fit(X, y)
# print('Coefficient: ', reg.coef_, '\tScore: ', reg.score(X, y))

print('\n******************************* C. Values of the variables ******************************* ')
text_for_txt_file = ''
for jj in range(len(vars_names)):
    name = vars_names[jj]
    variance = []
    for kk in range(len(n_data_points_per_session)-1):
        var_values_in_session = variables[jj][n_data_points_per_session[kk]:n_data_points_per_session[kk+1]]
        variance.append(statistics.variance([int(ele) for ele in var_values_in_session]))
        var_vals = '{} - session {} \t variance: {} \t values: {}'.format((name + ' ' * 15)[:15], kk,
                                                                          round(variance[-1], 3), var_values_in_session)
        print(var_vals)
        text_for_txt_file += var_vals + '\n'
    text_for_txt_file += '\n'
f = open(str(file_names.get_name_of_folder() / 'var_values_{}.txt'.format(name_participant)), 'w')
f.write(text_for_txt_file)
f.close()

# ************************************ Saving the model_id_out *********************************************************
data = bpd.generate_average_data_per_diff(N_difficulties, belief_difficulty_by_diff, metrics_by_diff)
if flatten_rld_metrics_per_diff:
    data = bpd.generate_data_for_df_w_normalise_rld_metrics_per_diff(metrics_by_diff_normalised, data)
df_overall = pd.DataFrame(data, columns=['Belief difficulty'] + rld_names_by_diff)
writer = excel_files.create_excel_file(file_names.get_name_of_metric_file_2_write(name_participant))
excel_files.save_df_to_excel_sheet(writer, df_overall, file_names.get_names_of_sheets(normalisation=False))

excel_files.save_df_to_excel_sheet(writer, pd.DataFrame(max_rld_values.values(), index=list(max_rld_values.keys())),
                                   file_names.get_names_of_sheets(normalisation=True))
