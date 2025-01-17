import copy

from experimentNao.interaction.performance_of_participant.participant_feedback import SheetNamesExtras
from experimentNao.model_ID.data_processing.excel_data_processing import get_specific_sheets_from_file


def set_values_of_vars_for_dm(dm_module, files, n_puzzles, set_influencer_values):
    """ sets the list of values of the variables of the decision-making module from the "files", in order to train and
    test the module. For each variable, the list of values corresponds to the sequence of realizations that this
    variable had over time during the interaction of the human with the robot.

    Parameters
    ----------
    dm_module : lib.tom_model.model_structure.decision_making_module.DecisionMakingModule
    files : List[pandas.io.excel._base.ExcelFile]
    n_puzzles : List[int]
    set_influencer_values : bool
    Returns
    -------

    """
    time_steps = []
    assert len(n_puzzles) == len(files)        # number of interactions
    for i in range(len(files)):
        n_time_steps_in_file = 0
        for action in dm_module.action_selector.outputs:
            if action.name == 'ask for easier game':
                ts = set_values_of_1_dm_variable_from_1_file(dm_module, files[i], action, set_influencer_values=False)
            else:
                ts = set_values_of_1_dm_variable_from_1_file(dm_module, files[i], action, set_influencer_values)
                n_time_steps_in_file += ts
        time_steps.append(range(n_time_steps_in_file))
    return time_steps


def set_values_of_1_var_for_dm(dm_module, files, n_puzzles, action_var, set_influencer_values):
    """ sets the list of values of each variable of the decision-making module from the "files", in order to train and
    test the module. For each variable, the list of values corresponds to the sequence of realizations that this
    variable had over time during the interaction of the human with the robot.

    Parameters
    ----------
    dm_module : lib.tom_model.model_structure.decision_making_module.DecisionMakingModule
    files : List[pandas.io.excel._base.ExcelFile]
    n_puzzles : List[int]
    action_var : experimentNao.declare_model.modules.declare_decision_making.ActionChessGame
    set_influencer_values : bool

    Returns
    -------
    List[range]
    """
    time_steps = []
    assert len(n_puzzles) == len(files)        # number of interactions
    for i in range(len(files)):
        ts = set_values_of_1_dm_variable_from_1_file(dm_module, files[i], action_var, set_influencer_values)
        time_steps.append(range(ts))
    return time_steps


def set_values_of_1_dm_variable_from_1_file(dm_module, file, variable_action, set_influencer_values=True):
    """ sets the list of values of each variable of the decision-making module from one file, in order to train and
    test the module. For each variable, the list of values corresponds to the sequence of realizations that this
    variable had over time during the interaction of the human with the robot.

    Parameters
    ----------
    dm_module : lib.tom_model.model_structure.decision_making_module.DecisionMakingModule
    file : pandas.io.excel._base.ExcelFile
    variable_action : experimentNao.declare_model.modules.declare_decision_making.ActionChessGame
    set_influencer_values : bool

    Returns
    -------
    int
    """
    if variable_action.name == 'quit game':
        dfs = set_values_quit(file, variable_action)
    elif variable_action.name == 'ask for help':
        dfs = set_values_ask_help(file, variable_action)
    elif variable_action.name in ['ask for easier game', 'ask for more difficult game']:
        dfs = set_values_ask_to_change_diff(file, variable_action)
    elif variable_action.name == 'skip puzzle':
        dfs = set_values_skip(file, variable_action)
    else:
        raise ValueError('Action given is none of the predefined actions')
    intention = set_corresponding_intention(dm_module, variable_action)
    if set_influencer_values:
        set_values_of_influencers(intention, dfs)
    return len(dfs)


def set_values_of_influencers(intention, dfs):
    """ sets the list of values of the influencers of the "intention" (beliefs and/or goals)

    Parameters
    ----------
    intention : experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame
    dfs : List[pandas.core.frame.DataFrame]
    """
    fill_value_of_variable(intention.goal, dfs)
    if intention.belief is not None:
        fill_value_of_variable(intention.belief, dfs)


def fill_value_of_variable(var, dfs):
    """ sets the list of values of one variable from the dataframes of the interaction (that came from 1 file).
    The list of values correspond to the sequence of values that this variable had over time during the interaction of
    the human with the robot.

    Parameters
    ----------
    var : lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal
    dfs : List[pandas.core.frame.DataFrame]
    """
    values = []
    for i in range(len(dfs)):                       # static representation for DM: (b_k, g_k) --> a_k
        var_row = dfs[i][dfs[i]['Var Name'] == var.name].iloc[0]
        values.append((var_row['Value']/10)*2-1)    # 2. step k = 2*DP + 1 with collection of data
    var.values = tuple(var.values) + tuple(values)


def set_values_quit(file, action):
    """  sets the list of values of the intention quit

    Parameters
    ----------
    file : pandas.io.excel._base.ExcelFile
    action : experimentNao.declare_model.modules.declare_decision_making.ActionChessGame

    Returns
    -------
    List[pandas.core.frame.DataFrame]
    """
    dfs_quit, dfs_mid_puzzles = get_dfs(file, quit_dfs=True), get_dfs(file, mid_puzzle=True)
    df_performance = get_dfs(file, performance=True)[0]
    for i in range(len(dfs_mid_puzzles)):
        action.actions_sequence.append(False)
    if df_performance['Quit'].values[-1]:        # check if the player quit in the last episode that was recorded
        assert len(dfs_quit) > 0
        action.actions_sequence.append(True)
    return dfs_mid_puzzles + dfs_quit


def set_values_ask_help(file, action):
    """  sets the list of values of the intention "ask for help"

    Parameters
    ----------
    file : pandas.io.excel._base.ExcelFile
    action : experimentNao.declare_model.modules.declare_decision_making.ActionChessGame

    Returns
    -------
    List[pandas.core.frame.DataFrame]
    """
    dfs_help, dfs_mid_puzzle = get_dfs(file, help_dfs=True), get_dfs(file, mid_puzzle=True)
    for i in range(len(dfs_help)):
        action.actions_sequence.append(True)
    for i in range(len(dfs_mid_puzzle)):
        action.actions_sequence.append(False)
    return dfs_help + dfs_mid_puzzle


def set_values_skip(file, action):
    """  sets the list of values of the intention "skip"

    Parameters
    ----------
    file : pandas.io.excel._base.ExcelFile
    action : experimentNao.declare_model.modules.declare_decision_making.ActionChessGame

    Returns
    -------
    List[pandas.core.frame.DataFrame]
    """
    dfs_mid_puzzle, df_end_of_puzzles = get_dfs(file, mid_puzzle=True), get_dfs(file, end_puzzle=True)
    df_performance = get_dfs(file, performance=True)[0]
    for i in range(len(dfs_mid_puzzle)):
        action.actions_sequence.append(False)
    # at the end of each puzzle, skip could either be active or not
    skipped_indices = df_performance.index[df_performance['skipped_puzzle']].tolist()
    skipped_steps = df_performance.loc[skipped_indices, 'Step'].values
    for i in range(len(df_end_of_puzzles)):
        action.actions_sequence.append(True if i in skipped_steps else False)
    return dfs_mid_puzzle + df_end_of_puzzles


def set_values_ask_to_change_diff(file, action):
    """  sets the list of values of one of the intentions 'ask for easier game' or 'ask for more difficult game'

    Parameters
    ----------
    file : pandas.io.excel._base.ExcelFile
    action : experimentNao.declare_model.modules.declare_decision_making.ActionChessGame

    Returns
    -------
    List[pandas.core.frame.DataFrame]
    """
    df_end_of_puzzles = get_dfs(file, end_puzzle=True)
    for i in range(len(df_end_of_puzzles)):
        data_series = df_end_of_puzzles[i].loc[df_end_of_puzzles[i]['Var Name'] == action.name]['Value']
        action.actions_sequence.append(data_series.values[0] != 0)
    return df_end_of_puzzles


def set_corresponding_intention(dm_module, action):
    """ sets the list of values of the action corresponding to the "intention"

    Parameters
    ----------
    dm_module : lib.tom_model.model_structure.decision_making_module.DecisionMakingModule
    action : experimentNao.declare_model.modules.declare_decision_making.ActionChessGame

    Returns
    -------
    experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame
    """
    for intention in dm_module.intention_selector.outputs:
        if action.name == intention.name:
            intention.intentions_sequence = copy.copy(action.actions_sequence)
            return intention


def get_dfs(file, end_puzzle=False, mid_puzzle=False, help_dfs=False, quit_dfs=False, performance=False):
    """ returns the dataframes with the dataframes with the flags (the boolean arguments of this function) corresponding
    to each intention.

    Parameters
    ----------
    file : pandas.io.excel._base.ExcelFile
    end_puzzle : bool
    mid_puzzle : bool
    help_dfs : bool
    quit_dfs : bool
    performance : bool

    Returns
    -------
    List[pandas.core.frame.DataFrame]
    """
    sheet_names_extras = SheetNamesExtras()
    if end_puzzle:
        return get_specific_sheets_from_file(file, name_must_contain=sheet_names_extras.puzzle_end)
    elif mid_puzzle:
        return get_specific_sheets_from_file(file, name_must_contain=sheet_names_extras.step,
                                             name_cant_contain=(sheet_names_extras.help, sheet_names_extras.quit,
                                                                sheet_names_extras.puzzle_end))
    elif help_dfs:
        return get_specific_sheets_from_file(file, name_must_contain=sheet_names_extras.help)
    elif quit_dfs:
        return get_specific_sheets_from_file(file, name_must_contain=sheet_names_extras.quit)
    elif performance:
        return get_specific_sheets_from_file(file, name_must_contain='Performance')
