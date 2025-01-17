from experimentNao.folder_path import data_folder_path
from lib import excel_files


def get_folder_path_old(folder):
    return data_folder_path + 'Participants IDed models - Preliminary Analysis/' + folder + '/'


def get_folder_path_new(folder, identifier):
    folder = folder if folder == '' else (folder + '/')
    return data_folder_path + 'Participants IDed models/' + identifier + '/' + folder


def write_comparison_excel_file(path, comparison_round, comparison_name, dfs_general_comp, dfs_individual_costs, participant_id):
    file_name = 'comparison_' + participant_id + '_' + str(comparison_round) + '_' + comparison_name + '.xlsx'
    writer = excel_files.create_excel_file(path + file_name)
    excel_files.save_df_to_excel_sheet(writer, dfs_general_comp, 'Comparison', index=False)
    excel_files.save_df_to_excel_sheet(writer, dfs_individual_costs, 'Individual costs comparison', index=False)
    writer.save()
    writer.close()


def get_dfs_from_file(general_path, overall_id_config):
    file_path = general_path + overall_id_config.get_model_id_file_name() + '.xlsx'
    df_sheets = excel_files.get_sheets_from_excel(file_path, sheet_names=['Overall Performance', 'Individual costs',
                                                                          'List of Parameters'])
    df_performance_t = df_sheets[0].iloc[[0]].reset_index(drop=True)
    df_performance_v = df_sheets[0].iloc[[1]].reset_index(drop=True)
    df_individual_costs_t = df_sheets[1].iloc[[0]].reset_index(drop=True)
    df_individual_costs_v = df_sheets[1].iloc[[1]].reset_index(drop=True)
    df_params = df_sheets[2]
    return df_performance_t, df_performance_v, df_individual_costs_t, df_individual_costs_v, df_params
