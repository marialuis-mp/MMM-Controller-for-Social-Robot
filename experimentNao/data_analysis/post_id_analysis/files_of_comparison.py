from experimentNao.model_ID.configs.model_configs import ModelConfigs as mc_new
from experimentNao.model_ID.configs.id_cog_modes import IdCogModes as id_modes


def get_best_sep_per_of_participant(participant_identifier):
    if participant_identifier == 'sVdskW':
        return [id_modes.SEP_PER_2, id_modes.SEP_PER_3], [mc_new.SIMPLEST_NO_SW_BIAS]
    if participant_identifier == 'KFgxTS':
        return [id_modes.SEP_PER_2, id_modes.SEP_PER_3], [mc_new.SIMPLEST_W_BIAS]
    if participant_identifier == 'M8z5Xu':
        return [id_modes.SEP_PER_2, id_modes.SEP_PER_3], [mc_new.SIMPLEST_W_BIAS]
    if participant_identifier == 'RD7TLs':
        return [id_modes.SEP_PER_2, id_modes.SEP_PER_3], [mc_new.SIMPLEST_W_BIAS]
    if participant_identifier == 'n9Ymja':
        return [id_modes.SEP_PER_2, id_modes.SEP_PER_3], [mc_new.SIMPLEST_W_BIAS_SLOW, mc_new.SIMPLEST_NO_SW_BIAS_SLOW]
    if participant_identifier == '6wYtDQ':
        return [id_modes.SEP_PER_2, id_modes.SEP_PER_3], [mc_new.SIMPLEST_W_BIAS]
    if participant_identifier == 'mJHZHu':
        return [id_modes.SEP_PER_2, id_modes.SEP_PER_3], [mc_new.SIMPLEST_W_BIAS]
    if participant_identifier == 'mJHZHu_NO':
        return [id_modes.SEP_PER_2, id_modes.SEP_PER_3], [mc_new.SIMPLEST_W_BIAS]
    if participant_identifier == '8QG5kg':
        return [id_modes.SEP_PER_2, id_modes.SEP_PER_3], [mc_new.SIMPLEST_W_BIAS]
    if participant_identifier == '8QG5kg_NO':
        return [id_modes.SEP_PER_2, id_modes.SEP_PER_3], [mc_new.SIMPLEST_W_BIAS]
    if participant_identifier == '8QG5kg_NO2':
        return [id_modes.SEP_PER_2, id_modes.SEP_PER_3], [mc_new.SIMPLEST_W_BIAS, mc_new.SIMPLEST_NO_SW_BIAS]
    if participant_identifier == 'PULP9U':
        return [id_modes.SEP_PER_2, id_modes.SEP_PER_3], [mc_new.SIMPLEST_NO_SW_BIAS]
    if participant_identifier == 'PULP9U_NO':
        return [id_modes.SEP_PER_2, id_modes.SEP_PER_3], [mc_new.SIMPLEST_NO_SW_BIAS]
    if participant_identifier == '7cPNcE':
        return [id_modes.SEP_PER_2, id_modes.SEP_PER_3], [mc_new.SIMPLEST_W_BIAS]


def get_comparison_configs(comparison_round, best_sep_per, best_config):
    current_folder = ''
    model_configs = [mc_new.DEFAULT_BIAS]
    id_cog_modes = [id_modes.ALL]
    simple_dyn = [True]
    incremental = [True]
    n_horizons = [1]
    normalise_rld_options = [False]
    if comparison_round == 'prelim_official':
        incremental = [True, False]
        id_cog_modes = [id_modes.ALL, id_modes.SEP_PER_2, id_modes.SEP_PER_3]
    elif comparison_round == 'id_modes':
        id_cog_modes = [id_modes.ALL, id_modes.SEP_PER_1, id_modes.SEP_PER_2, id_modes.SEP_PER_3]
    elif comparison_round == 'simple_model':
        model_configs = [mc_new.DEFAULT_BIAS, mc_new.SIMPLEST_W_BIAS]
        id_cog_modes = best_sep_per
    elif comparison_round == 'extra_simple':
        model_configs = [mc_new.SIMPLEST_W_BIAS, mc_new.NO_SW_BIAS, mc_new.SIMPLEST_NO_SW_BIAS]
        id_cog_modes = best_sep_per
    elif comparison_round == 'cost_n':
        model_configs = best_config
        id_cog_modes = best_sep_per
        n_horizons = [1, 2]
    elif comparison_round == 'special_incr':
        model_configs = [mc_new.DEFAULT_BIAS,
                         mc_new.SIMPLEST_W_BIAS, mc_new.SIMPLEST_NO_SW_BIAS,
                         mc_new.SIMPLEST_W_BIAS_SLOW, mc_new.SIMPLEST_NO_SW_BIAS_SLOW]
        id_cog_modes = best_sep_per
        incremental = [False, True]
    return current_folder, model_configs, id_cog_modes, simple_dyn, incremental, n_horizons, normalise_rld_options
