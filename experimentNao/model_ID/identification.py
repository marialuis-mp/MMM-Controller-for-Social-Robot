from experimentNao.declare_model import declare_entire_model as dem
from experimentNao.model_ID.cognitive import identification_cog_all_module as id_cog_all, \
    identification_cog_var_by_var as id_cog_1_by_1, identification_cog_percept as id_cog_per
from experimentNao.model_ID.configs import model_configs, id_cog_modes
from experimentNao.model_ID.data_processing import pick_train_data
from experimentNao.model_ID.decision_making import identification_dm_all_model as id_dm_all, \
    identification_dm_var_by_var as id_dm_1_by_1
from experimentNao.model_ID.decision_making.identification_dm import OptMode


def train_and_valid_dm(writer, readers, n_puzzles, id_conf, my_random, train_mode):
    """

    Parameters
    ----------
    writer : pandas.io.excel._openpyxl.OpenpyxlWriter
        file to where the results are written to
    readers : List[pandas.io.excel._base.ExcelFile]
        output files of the training session, which correspond to the train and test data
    n_puzzles : List[int]
        number of puzzles that were played by the players
    id_conf : experimentNao.model_ID.configs.overall_config.IDConfig
        configuration of the identification process
    my_random : random.Random
        the random variable (for traceability)
    train_mode : experimentNao.model_ID.decision_making.identification_dm.OptMode
    """
    print('*********  ID Decision Making ' + ('GA' if train_mode == OptMode.GENETIC_ALGORITHM else 'GD') + ' *********')
    id_entire_model_at_once = False
    dm_module = dem.get_model_from_config(id_conf, dem.get_normalization_values_of_rld(None)).decision_making_module
    train_data_settings = pick_train_data.get_default_settings()
    if id_entire_model_at_once:
        id_engine = id_dm_all.DMIdentificationAll(dm_module, n_puzzles, train_data_settings, train_mode, my_random,
                                                  writer, readers)
    else:
        id_engine = id_dm_1_by_1.DMIdentification1by1(dm_module, n_puzzles, train_data_settings, train_mode, my_random,
                                                      writer, readers)
    id_engine.identify_and_test()


def train_and_validate_cognitive_module(writer, readers, n_puzzles, random, overall_id_config, delft_blue,
                                        short_mode, prune=False):
    """ manages the identification of the parameters of the cognitive and perception module

    Parameters
    ----------
    writer : pandas.io.excel._openpyxl.OpenpyxlWriter
        file to where the results are written to
    readers : List[pandas.io.excel._base.ExcelFile]
        output files of the training session, which correspond to the train and test data
    n_puzzles : List[int]
        number of puzzles that were played by the players
    random : random.Random
        the random variable (for traceability)
    overall_id_config : experimentNao.model_ID.configs.overall_config.IDConfig
        configuration of the identification process
    delft_blue : bool
        whether the programme is being run in the supercomputer (set as False, for users outside the TU Delft)
    short_mode : bool
        for debugging
    prune : bool
    """
    print('********* ID Cognitive Model *********\n', overall_id_config.get_model_id_file_name())
    # Get model
    included_vars = model_configs.get_model_configuration(overall_id_config.model_config, overall_id_config.incremental)
    max_rld_values = dem.get_normalization_values_of_rld(readers, from_id=False)
    tom_model = dem.declare_model(included_vars, max_rld_values, overall_id_config)
    # Identification Engine
    if overall_id_config.id_cog_mode == id_cog_modes.IdCogModes.ALL:
        id_engine = id_cog_all.CognitiveIdAll(tom_model, n_puzzles, writer, readers, prune, included_vars, random,
                                              overall_id_config, short_mode, verbose=3, delft_blue=delft_blue)
    elif overall_id_config.id_cog_mode == id_cog_modes.IdCogModes.VAR_BY_VAR:
        id_engine = id_cog_1_by_1.CognitiveId1by1(tom_model, n_puzzles, writer, readers, prune, random,
                                                  overall_id_config, short_mode, verbose=1)
    else:
        id_engine = id_cog_per.CognitiveIdPercept(tom_model, n_puzzles, writer, readers, prune, included_vars, random,
                                                  overall_id_config, short_mode, verbose=3, delft_blue=delft_blue,
                                                  reuse_data_sep_3=False)
    id_engine.identify_and_test()
