import math

from experimentNao.model_ID.data_processing import excel_data_processing
from experimentNao.declare_model import chess_interaction_data as ci_data
from experimentNao.interaction.performance_of_participant.participant_feedback import SheetNamesExtras


def set_values_of_vars_for_cognitive_module(tom_model, files, number_puzzles, hidden_vars, simplified_dynamics, normalise_rld_mid_steps):
    """ sets the list of values of each variable of the model "tom_model" from the "files", in order to train the model.
    For each variable, the list of values correspond to the sequence of realizations that this variable had over time
    during the interaction of the human with the robot.

    Parameters
    ----------
    tom_model : experimentNao.declare_model.declare_entire_model.ToMModelChessSimpleDyn
    files : List[pandas.io.excel._base.ExcelFile]
    number_puzzles : List[int]
    hidden_vars : List[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]
    simplified_dynamics : bool
    normalise_rld_mid_steps : bool

    Returns
    -------
    List[List[float]]
    """
    time_steps = []
    assert len(number_puzzles) == len(files)        # number of interactions
    cognitive = tom_model.cognitive_module
    state_variables = cognitive.get_beliefs() + cognitive.get_goals() + cognitive.get_emotions()
    for i in range(len(files)):
        variables = set_values_of_cognitive_variables_from_1_file(tom_model, files[i], state_variables, hidden_vars,
                                                                  simplified_dynamics)
        if simplified_dynamics:
            set_values_of_rld_variables_for_simplified_dynamics(tom_model, files[i], normalise_rld_mid_steps)
        else:
            set_values_of_rld_variables(tom_model, files[i], normalise_rld_mid_steps)
        time_steps.append(get_time_steps(input_file=files[i]))
    for var in state_variables:
        var.values = tuple(var.values)
    # Some assertions
    assert len(tom_model.cognitive_module.state_vars[0].values) == len(tom_model.cognitive_module.state_vars[1].values)
    if simplified_dynamics:
        assert len(tom_model.cognitive_module.state_vars[0].values) == len(tom_model.perception_module.perceptual_access.inputs.sequence_of_inputs)
        assert sum(len(sublist) for sublist in time_steps) == len(tom_model.cognitive_module.state_vars[0].values)
    else:
        assert len(tom_model.cognitive_module.state_vars[0].values) == len(tom_model.perception_module.perceptual_access.inputs.sequence_of_inputs)
        assert sum(len(sublist) for sublist in time_steps)*2 == len(tom_model.cognitive_module.state_vars[0].values)
    return time_steps


def set_values_of_cognitive_variables_from_1_file(tom_model, file, state_variables, hidden_vars, simplified_dynamics):
    """ sets the list of values of each variable of the model "tom_model" from one file, in order to train the model.
    For each variable, the list of values correspond to the sequence of realizations that this variable had over time
    during one interaction of the human with the robot.

    Parameters
    ----------
    tom_model : experimentNao.declare_model.declare_entire_model.ToMModelChessSimpleDyn
    file : pandas.io.excel._base.ExcelFile
    state_variables : Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion]
    hidden_vars : List[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]
    simplified_dynamics : bool

    Returns
    -------
    Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion]
    """
    sheet_names = SheetNamesExtras()
    dfs = excel_data_processing.get_specific_sheets_from_file(file, name_must_contain=sheet_names.step,
                                                              name_cant_contain=[sheet_names.help, sheet_names.quit])
    for var in state_variables:
        if var in hidden_vars:
            fill_values_of_reward_belief_as_hidden_var(var, file, simplified_dynamics)
        else:
            fill_values_of_variable(var, dfs, simplified_dynamics)
    for var in tom_model.cognitive_module.get_all_slow_dynamics_vars():
        var.values = (1, ) * len(state_variables[1].values)
    return state_variables


def fill_values_of_reward_belief_as_hidden_var(var, file, simplified_dynamics):
    """ fills values of the belief "nao gives reward" with the corresponding values of the real life data
    "nao gives reward", to be used when we consider this belief a hidden variable.

    Parameters
    ----------
    var : lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief
    file : pandas.io.excel._base.ExcelFile
    simplified_dynamics : bool
    """
    assert 'reward' in var.name
    values = []
    df = excel_data_processing.get_specific_sheets_from_file(file, name_must_contain='Performance')[0]
    for i in range(len(df)):
        if not df.at[i, 'Quit']:
            if not simplified_dynamics:
                values.append(None)
            values.append(1 if df.at[i, 'reward_given'] else -1)
    var.values = var.values + values


def fill_values_of_variable(var, dfs, simplified_dynamics):
    """ sets the list of values of one variable from the dataframes of the interaction (that came from 1 file).
    The list of values correspond to the sequence of values that this variable had over time during the interaction of
    the human with the robot.

    Parameters
    ----------
    var : Union[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal]
    dfs : List[pandas.core.frame.DataFrame]
    simplified_dynamics : bool
    """
    values = []
    for i in range(len(dfs)):
        if not simplified_dynamics:            # if not simplified -> for each data point DP collected we have:
            values.append(None)                                     # 1. step k = 2*DP with no collection of data
        var_row = dfs[i][dfs[i]['Var Name'] == var.name].iloc[0]    # 2. step k = 2*DP + 1 with collection of data
        values.append((var_row['Value']/10)*2-1)
    var.values = var.values + values


def set_values_of_rld_variables(tom_model, file, normalise_rld_mid_steps):
    """ sets the values of the real life data of 1 interaction when simplified dynamics variables are not used.

    Parameters
    ----------
    tom_model : experimentNao.declare_model.declare_entire_model.ToMModelChessSimpleDyn
    file : pandas.io.excel._base.ExcelFile
    normalise_rld_mid_steps : bool
    """
    df = excel_data_processing.get_specific_sheets_from_file(file, name_must_contain='Performance')
    rld = tom_model.perception_module.perceptual_access.inputs
    rld.sequence_of_inputs.append(None)
    assert len(df) == 1
    df = df[0]
    next_chess_data_collected = ci_data.ChessInteractionData().get_from_data_frame(df.iloc[[0]])   # starting u (u_2)
    if check_if_to_normalise_mid_step(normalise_rld_mid_steps, df, i=0):
        next_chess_data_collected.normalise_mid_step()
    # rld = get_initial_u(rld, next_chess_data_collected)
    for i in range(len(df)):             # for each data point DP collected we have:
        if not df.at[i, 'Quit']:
            this_chess_data_collected = next_chess_data_collected   # starting u
            # 1. step k = 2*DP with collection of data
            rld.add_input_to_sequence_of_inputs(this_chess_data_collected)
            if i + 1 == len(df):
                break
            # 2. step k = 2*DP + 1 with interpolated data
            if not df.at[i+1, 'Quit']:
                next_time_step_row = df.iloc[[i + 1]]
                next_chess_data_collected = ci_data.ChessInteractionData().get_from_data_frame(next_time_step_row)
                if check_if_to_normalise_mid_step(normalise_rld_mid_steps, df, i=i + 1):
                    next_chess_data_collected.normalise_mid_step()
                chess_data_interp = set_intermediate_fictitious_rld(this_chess_data_collected, next_chess_data_collected,
                                                                    next_time_step_row)
                rld.add_input_to_sequence_of_inputs(chess_data_interp)
    tom_model.perception_module.perceptual_access.inputs.set_current_input_from_sequence(0)


def set_values_of_rld_variables_for_simplified_dynamics(tom_model, file, normalise_rld_mid_steps):
    """ sets the values of the real life data of 1 interaction when simplified dynamics variables are used.

    Parameters
    ----------
    tom_model : experimentNao.declare_model.declare_entire_model.ToMModelChessSimpleDyn
    file : pandas.io.excel._base.ExcelFile
    normalise_rld_mid_steps : bool
    """
    df = excel_data_processing.get_specific_sheets_from_file(file, name_must_contain='Performance')
    rld = tom_model.perception_module.perceptual_access.inputs
    assert len(df) == 1
    df = df[0]
    for i in range(len(df)):
        if not df.at[i, 'Quit']:
            data_collected = ci_data.ChessInteractionData().get_from_data_frame(df.iloc[[i]])
            if check_if_to_normalise_mid_step(normalise_rld_mid_steps, df, i):
                data_collected.normalise_mid_step()
            rld.add_input_to_sequence_of_inputs(data_collected)
    tom_model.perception_module.perceptual_access.inputs.set_current_input_from_sequence(0)


def check_if_to_normalise_mid_step(normalise_rld_mid_steps, performance_df, i):
    """ check whether, according to current settings, the current step should be normalized. Only the middle steps are
    normalized, and only when normalise_rld_mid_steps is True.

    Parameters
    ----------
    normalise_rld_mid_steps : bool
    performance_df : pandas.core.frame.DataFrame
    i : int

    Returns
    -------
    bool
    """
    if normalise_rld_mid_steps:
        try:
            is_end_of_puzzle = (math.floor(performance_df.at[i, 'Step']) != math.floor(performance_df.at[i + 1, 'Step']))
        except KeyError:
            is_end_of_puzzle = True
        return not is_end_of_puzzle
    return False


def set_intermediate_fictitious_rld(this_chess_data_collected, next_chess_data_collected, next_time_step_row):
    """ generates an intermediate real-life data point by interpolating between the current and next rld point.
    This function generates the rld point for a middle of the puzzle.

    Parameters
    ----------
    this_chess_data_collected : experimentNao.declare_model.modules.declare_perception_module.ChessRLD
    next_chess_data_collected : experimentNao.declare_model.modules.declare_perception_module.ChessRLD
    next_time_step_row : pandas.DataFrame

    Returns
    -------

    """
    if '.0' in str(next_time_step_row.iloc[0]['Step']):  # if this is the first u of a puzzle
        previous_data_point = get_a_data_point_for_start_of_puzzle(next_chess_data_collected)
    else:
        previous_data_point = this_chess_data_collected
    return ci_data.interpolate_between_two_points(previous_data_point, next_chess_data_collected)


def get_a_data_point_for_start_of_puzzle(next_chess_data_collected):
    """ generates an intermediate real-life data point by interpolating with the next rld point.
    This function generates the rld point for the beginning of the puzzle.

    Parameters
    ----------
    next_chess_data_collected : experimentNao.declare_model.modules.declare_perception_module.ChessRLD

    Returns
    -------

    """
    data_point = ci_data.ChessInteractionData()
    data_point.fill_data(0, [0], next_chess_data_collected.puzzle_difficulty, prop_moves_revealed=0, time_2_solve=0,
                         nao_helping=next_chess_data_collected.nao_helping,
                         nao_offering_reward=next_chess_data_collected.nao_offering_rewards,
                         reward_given=False, skipped=False)
    return data_point


def get_time_steps(input_file):
    """ returns how many time steps (a.k.a.data points) were collected on the interaction that generated "input_file"

    Parameters
    ----------
    input_file : pandas.io.excel._base.ExcelFile

    Returns
    -------
    List[float]
    """
    sheet_name_suffix = SheetNamesExtras()
    list_of_time_steps = []
    for sheet_name in input_file.sheet_names:
        if sheet_name_suffix.step in sheet_name and sheet_name_suffix.help not in sheet_name and sheet_name_suffix.quit not in sheet_name:
            for sub_string_to_remove in (sheet_name_suffix.step, sheet_name_suffix.puzzle_end, sheet_name_suffix.quit):
                sheet_name = sheet_name.replace(sub_string_to_remove, '')
            list_of_time_steps.append(float(sheet_name))
    return list_of_time_steps
