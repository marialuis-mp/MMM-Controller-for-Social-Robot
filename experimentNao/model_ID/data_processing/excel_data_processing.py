import copy

import pandas as pd

from experimentNao import folder_path
from experimentNao.declare_model import chess_interaction_data
from experimentNao.model_ID.configs import id_cog_modes
from lib import excel_files


def preprocess(overall_id_config):
    """ preprocess the necessary Excel files for the identification process, such as opening the reader files, creating
    the writer file, and extracting the number of puzzles played in each interaction

    Parameters
    ----------
    overall_id_config : experimentNao.model_ID.configs.overall_config.IDConfig

    Returns
    -------
    Tuple[pandas.io.excel._openpyxl.OpenpyxlWriter, List[pandas.io.excel._base.ExcelFile], List[int]]
    """
    path = folder_path.output_folder_path / 'model_id_out'
    writer = excel_files.create_excel_file(str(path / overall_id_config.get_model_id_file_name()))
    reader_files, n_puzzles = pre_process_participant_input_files(overall_id_config.participant_id)
    return writer, reader_files, n_puzzles


def pre_process_participant_input_files(participant_id):
    """ extracts the reader files (one per interaction) and the unmber of puzzles played in each interaction.

    Parameters
    ----------
    participant_id : str
        identifier of the participant

    Returns
    -------
    Tuple[List[pandas.io.excel._base.ExcelFile], List[int]]
    """
    reader_files, reader_files_names = get_input_files(participant_id)
    n_puzzles = list()
    for i in range(len(reader_files)):
        puzzle_list_df = get_specific_sheets_from_file(reader_files[i], 'Puzzle list', name_cant_contain=[])[0]
        n_puzzles.append(len(puzzle_list_df))
    return reader_files, n_puzzles


def get_input_files(participant_identifier):
    """ extracts the reader files (one per interaction) where the data from the interactions that will be used to train
    and test the model is, and the name of the files

    Parameters
    ----------
    participant_identifier : str

    Returns
    -------
    Tuple[List[pandas.io.excel._base.ExcelFile], List[str]]
    """
    files, file_names = list(), list()  # to save
    interaction = 0
    while True:
        interaction += 1
        try:
            file_name = participant_identifier + '_' + str(interaction)
            files.append(get_excel_file(file_name))
            file_names.append(file_name)
            pass
        except FileNotFoundError:
            break
    return files, file_names


def get_excel_file(interaction_identifier):
    """ returns the Excel file generated in the training interactions with participant "participant_name"

    Parameters
    ----------
    interaction_identifier : str
        identifier of the participant + number of interaction

    Returns
    -------
    pandas.io.excel._base.ExcelFile
    """
    path = folder_path.output_folder_path / 'replies_participants' / 'training_sessions' / 'to_id'
    return excel_files.get_excel_file(path / ('Reply_' + interaction_identifier + '.xlsx'))


def write_list_of_vars_and_id_tags_2_excel(tom_model, writer):
    """ writes the list of variables of the cognitive model, including their tag (position of the variable in the list
     of all variables), their type (belief, goal, etc...), and their name, in a sheet of the write Excel file

    Parameters
    ----------
    tom_model : experimentNao.declare_model.declare_entire_model.ToMModelChessSimpleDyn
    writer : pandas.io.excel._openpyxl.OpenpyxlWriter
    """
    data2append = []
    for var in tom_model.get_all_variables():
        data2append.append([var.tag, str(type(var).__name__), var.name])
    df = pd.DataFrame(data2append, columns=['tag', 'type', 'name'])
    excel_files.save_df_to_excel_sheet(writer, df, 'List of Vars')


def write_list_of_parameters_2_excel(writer, df_params_list):
    """ writes the list of parameters in a sheet of the writer Excel file

    Parameters
    ----------
    writer :
    df_params_list :
    """
    excel_files.save_df_to_excel_sheet(writer, df_params_list, 'List of Parameters')


def get_specific_sheets_from_file(input_file, name_must_contain, name_cant_contain=[]):
    """ gets the N dataframe corresponding to the N sheets Excel files whose names contain "name_must_contain" and
    do not contain "name_cant_contain"

    Parameters
    ----------
    input_file : pandas.io.excel._base.ExcelFile
    name_must_contain : str
        string that the sheet(s) name(s) must contain
    name_cant_contain : List[str]
        list of strings that the sheet(s) name(s) cannot contain

    Returns
    -------
    List[pandas.core.frame.DataFrame]
    """
    list_of_dfs = []
    for sheet_name in input_file.sheet_names:
        if name_must_contain in sheet_name:
            if all(forbidden_words not in sheet_name for forbidden_words in name_cant_contain):
                df = input_file.parse(sheet_name)
                list_of_dfs.append(df)
    return list_of_dfs


def open_results_from_sep_per_1(overall_id_config):
    """ opens the Excel file that contains the results from the model identification done with certain configurations
    and id_mode=SEP_PER_1, and returns its sheets.


    Parameters
    ----------
    overall_id_config : experimentNao.model_ID.configs.overall_config.IDConfig

    Returns
    -------

    """
    overall_id_config_copy = copy.deepcopy(overall_id_config)
    overall_id_config_copy.id_cog_mode = id_cog_modes.IdCogModes.SEP_PER_1
    file = overall_id_config_copy.get_model_id_file()
    return get_specific_sheets_from_file(file, name_must_contain='ID')


def get_normalization_values_of_rld_from_participant_file(participant_data_files):
    """ gets the values that will be used to normalise the real life data of each participant, depending on the
    (maximum) values of the real life data during the interaction with this participant. This function extracts the
    normalisation data from the files directly.

    Parameters
    ----------
    participant_data_files : List[pandas.io.excel._base.ExcelFile]

    Returns
    -------
    Dict[str, int]
    """
    # Get data from file
    dfs_performance = []
    for file in participant_data_files:
        dfs_performance.append(get_specific_sheets_from_file(file, 'Performance')[0])
    if len(dfs_performance) == 0:
        raise TypeError("Make sure there us at least one file corresponding to the participant output in one "
                        "interaction, in order to identify the model")
    dfs_performance = pd.concat(dfs_performance)
    # Construct dict
    rld_max_values = dict()
    for name in chess_interaction_data.get_data_titles()[:5]:
        if name == 'n_wrong_attempts':
            all_wrong_attempts = list(dfs_performance['n_wrong_attempts'])
            values = [sum([int(v if len(v) > 0 else 0) for v in value_wa[1:-1].split(', ')]) for value_wa in all_wrong_attempts]
        else:
            values = list(dfs_performance[name])
        max_value = max(values)
        rld_max_values[name] = max_value if max_value != 0 else 1
    return rld_max_values


def get_normalization_values_of_rld_from_id_file(id_data_file):
    """ gets the values that will be used to normalise the real life data of each participant, that were previously
    extracted depending on the (maximum) values of the real life data during the interaction with this participant by
    "get_normalization_values_of_rld_from_participant_file" and stored in a new file.

    Parameters
    ----------
    id_data_file : pandas.io.excel._base.ExcelFile

    Returns
    -------

    """
    df_max_rld = get_specific_sheets_from_file(id_data_file, 'Normalization RLD')[0]
    keys = df_max_rld.iloc[:, 0]
    values = df_max_rld.iloc[:, 1]
    return dict(zip(keys, values))


def get_value_of_row_that_satisfies_condition_in_another_column(df, name_column_of_condition, value_condition,
                                                                name_column_of_interest):
    """ In a dataframe df, returns value of column 'name_column_of_interest' in row R, where row R is
    the row where column 'name_column_of_condition' has value 'value_condition'.

    Parameters
    ----------
    df :
    name_column_of_condition :
    value_condition :
    name_column_of_interest :

    Returns
    -------

    """
    index_belief = df.index[df[name_column_of_condition] == value_condition].to_list()
    cell = df.iloc[index_belief][name_column_of_interest]
    return cell.iloc[0]
