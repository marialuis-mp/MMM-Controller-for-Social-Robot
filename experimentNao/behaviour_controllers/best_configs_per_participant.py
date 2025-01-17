from experimentNao.model_ID.configs.model_configs import ModelConfigs as mc_new
from experimentNao.model_ID.configs.id_cog_modes import IdCogModes as id_modes
from experimentNao.model_ID.configs import train_test_config as tc


def get_best_configs_per_participant(participant_identifier):
    """ returns the best model configuration for each participant of the experiment, according to the defined protocol

    Parameters
    ----------
    participant_identifier : str

    Returns
    -------
    Tuple[experimentNao.model_ID.configs.id_cog_modes.IdCogModes, experimentNao.model_ID.configs.model_configs.ModelConfigs, experimentNao.model_ID.configs.train_test_config.TrainingSets, int]
    """
    if participant_identifier == 'sVdskW':
        return id_modes.SEP_PER_3, mc_new.SIMPLEST_NO_SW_BIAS, tc.TrainingSets.B, 1
    if participant_identifier == 'KFgxTS':
        return id_modes.SEP_PER_2, mc_new.SIMPLEST_W_BIAS, tc.TrainingSets.B, 1
    if participant_identifier == 'M8z5Xu':
        return id_modes.SEP_PER_2, mc_new.SIMPLEST_W_BIAS, tc.TrainingSets.B, 1
    if participant_identifier == 'RD7TLs':
        return id_modes.SEP_PER_3, mc_new.SIMPLEST_W_BIAS, tc.TrainingSets.A, 2
    if participant_identifier == 'n9Ymja':
        return id_modes.SEP_PER_3, mc_new.SIMPLEST_NO_SW_BIAS_SLOW, tc.TrainingSets.A, 1
    if participant_identifier == '6wYtDQ':
        return id_modes.SEP_PER_3, mc_new.SIMPLEST_W_BIAS, tc.TrainingSets.A, 2
    if participant_identifier == 'mJHZHu':
        return id_modes.SEP_PER_3, mc_new.SIMPLEST_W_BIAS, tc.TrainingSets.B, 2
    if participant_identifier == '8QG5kg':
        return id_modes.SEP_PER_3, mc_new.SIMPLEST_W_BIAS, tc.TrainingSets.A, 2
    if participant_identifier == 'PULP9U':
        return id_modes.SEP_PER_3, mc_new.SIMPLEST_NO_SW_BIAS, tc.TrainingSets.A, 1
    if participant_identifier == '7cPNcE':
        return id_modes.SEP_PER_3, mc_new.SIMPLEST_W_BIAS, tc.TrainingSets.A, 1
    return id_modes.SEP_PER_3, mc_new.DEFAULT, tc.TrainingSets.B, 1
