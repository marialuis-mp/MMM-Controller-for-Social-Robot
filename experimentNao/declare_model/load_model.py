import copy
import random

import experimentNao.declare_model.modules.declare_cognitive_module
import experimentNao.model_ID.decision_making.parameters_manager
from experimentNao.data_analysis.post_id_analysis import paths_and_files
from experimentNao.data_analysis.pre_process_data import file_names
from experimentNao.model_ID.cognitive import parameters_manager as pm
from experimentNao.model_ID.configs import model_configs
from lib import excel_files
from lib.algorithms.gradient_descent import parameters2optimise as params, settings as s_gd


def load_parameters_in_a_model(tom_model, included_variables, overall_id_config, parameters_cog_df, parameters_dm_df):
    """ generates the tom_model, and loads it from parameters from the dataframes "parameters_cog_df" and
    "parameters_dm_df" in the tom_model

    Parameters
    ----------
    tom_model : experimentNao.declare_model.declare_entire_model.ToMModelChessSimpleDyn
    included_variables : experimentNao.declare_model.included_elements.IncludedElements
    overall_id_config : experimentNao.model_ID.configs.overall_config.IDConfig
    parameters_cog_df : pandas.core.frame.DataFrame
    parameters_dm_df : pandas.core.frame.DataFrame

    Returns
    -------
    Tuple[List[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], List[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]]
    """
    ided_vars, hidden_vars = tom_model.cognitive_module.get_vars_2_id_and_hidden_vars(included_variables)
    vars_w_links_to_id = tom_model.cognitive_module.get_vars_w_link_to_id(ided_vars, overall_id_config.simple_dynamics)
    perception_params_1st = 'RLD' in parameters_cog_df['Influencer'][0]  # check if perception is first
    set_parameters(parameters_cog_df, tom_model, vars_w_links_to_id, random, perception_params_1st)
    experimentNao.model_ID.decision_making.parameters_manager.set_parameters(parameters_dm_df, tom_model.decision_making_module)
    return ided_vars, hidden_vars


def get_dfs_with_files(file_id_cog, file_id_dm):
    """ returns the dataframes with information from the files regarding the values of the parameter of each module

    Parameters
    ----------
    file_id_cog :
    file_id_dm :

    Returns
    -------

    """
    sheet_name = ('List of Parameters',)
    parameters_cog_df = excel_files.get_sheets_from_excel(None, input_file=file_id_cog, sheet_names=sheet_name)[0]
    parameters_dm_df = excel_files.get_sheets_from_excel(None, input_file=file_id_dm, sheet_names=sheet_name)[0]
    return parameters_cog_df, parameters_dm_df


def get_files_with_parameters_and_metrics(id_config):
    """ gets the files that contains the parameters and metrics of a participant, with the "id_config" chosen

    Parameters
    ----------
    id_config : experimentNao.model_ID.configs.overall_config.IDConfig

    Returns
    -------
    Tuple[pandas.io.excel._base.ExcelFile, pandas.io.excel._base.ExcelFile, pandas.io.excel._base.ExcelFile, experimentNao.declare_model.included_elements.IncludedElements]
    """
    id_config_dm = copy.deepcopy(id_config)
    id_config_dm.cog_2_id = False
    general_path = paths_and_files.get_folder_path_new('', id_config.participant_id)
    file_cog = id_config.get_model_id_file_from_overall_path(general_path)
    file_dm = id_config_dm.get_model_id_file_from_overall_path(general_path)
    file_metrics = excel_files.get_excel_file(file_names.get_name_of_metric_file_2_read(id_config.participant_id))
    included_variables = model_configs.get_model_configuration(id_config.model_config, id_config.incremental)
    # Check if 100% params were identified
    df_overall = excel_files.get_sheets_from_excel(None, ['Overall Performance'], file_cog)[0]
    assert df_overall['IDed Params'][0] == df_overall['N params'][0]
    return file_cog, file_dm, file_metrics, included_variables


def set_parameters(parameters_df, tom_model, vars_w_links_to_id, random, perception_first):
    """ sets the parameters of the cognition and perception modules

    Parameters
    ----------
    parameters_df : pandas.core.frame.DataFrame
    tom_model : experimentNao.declare_model.declare_entire_model.ToMModelChessSimpleDyn
    vars_w_links_to_id : Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion]
    random : module
    perception_first : bool
    """
    parameters_list = []
    for par in range(len(parameters_df)):
        value = parameters_df.iloc[par]['Values']
        value = value if not isinstance(value, bool) else (1 if value is True else -1)
        parameters_list.append(params.Parameter2Optimise(-1, 1, value=value))  # min & max values are not relevant here
    parameters_manager = pm.ParametersManager(tom_model, random, include_slow_dyn=False)
    if perception_first:
        n_params_percept, n_params_cog = parameters_manager.count_parameters(vars_w_links_to_id, s_gd.Settings(0, 0, False, 0, 0))
        params_percept = parameters_list[:n_params_percept]
        params_cognition = parameters_list[n_params_percept:]
        parameters_manager.include_cognitive, parameters_manager.include_perception = False, True
        parameters_manager.set_values_of_parameters(params_percept, vars_w_links_to_id)
        parameters_manager.include_cognitive, parameters_manager.include_perception = True, False
        parameters_manager.set_values_of_parameters(params_cognition, vars_w_links_to_id)
    else:
        parameters_manager.set_values_of_parameters(parameters_list, vars_w_links_to_id)
