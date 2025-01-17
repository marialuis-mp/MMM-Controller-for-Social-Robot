from lib.tom_model.model_elements.variables import fst_dynamics_variables as fst_dyn, slow_dynamics_variables as slw_dyn
from lib.tom_model.model_declaration_auxiliary import variables_declaration_aux as declare
from experimentNao.declare_model import chess_interaction_data as int_data
from experimentNao.declare_model.modules import declare_perception_module as declare_percept, \
    declare_decision_making as declare_dm


def declare_all_variables(included_vars):
    """ declares all the variables of the tom model

    Parameters
    ----------
    included_vars : experimentNao.declare_model.included_elements.IncludedElements

    Returns
    -------
    Tuple[Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal], Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias], Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.RationallyPerceivedKnowledge], Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge], Dict[str, lib.tom_model.model_elements.variables.slow_dynamics_variables.GeneralPreferences], Dict[str, lib.tom_model.model_elements.variables.slow_dynamics_variables.PersonalityTraits], List[experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame], List[experimentNao.declare_model.modules.declare_decision_making.ActionChessGame], experimentNao.declare_model.modules.declare_perception_module.ChessRLD, experimentNao.declare_model.modules.declare_perception_module.ChessPerceivedData, experimentNao.declare_model.modules.declare_perception_module.ChessRationallyPerceivedKnowledge]
    """
    beliefs, goals, emotions, biases, rpk, pks, gps, pts = declare_cognitive_vars(included_vars)
    intentions, actions = declare_decision_making_vars(beliefs, goals, included_vars)
    rld, pd, rpk_set = declare_perception_vars(rpk)

    return beliefs, goals, emotions, biases, rpk, pks, gps, pts, intentions, actions, rld, pd, rpk_set


def declare_cognitive_vars(included_vars):
    """ declares the variables of the cognitive module of the tom model

    Parameters
    ----------
    included_vars : experimentNao.declare_model.included_elements.IncludedElements

    Returns
    -------
    Tuple[Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal], Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias], Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.RationallyPerceivedKnowledge], Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge], Dict[str, lib.tom_model.model_elements.variables.slow_dynamics_variables.GeneralPreferences], Dict[str, lib.tom_model.model_elements.variables.slow_dynamics_variables.PersonalityTraits]]
    """
    beliefs_names = ('game difficulty', )
    goals_names = ('quit game', )
    emotions_names = ('confident/frustrated', 'interested/bored')
    gps_names = ['chess preference']
    pts_names = ['self confident', 'focused']
    if included_vars.belief_nao_helping:
        beliefs_names = beliefs_names + ('nao helping', )
    if included_vars.belief_made_progress:  # extra variables that are only included depending on 'included_vars'
        beliefs_names = beliefs_names + ('made progress', )
    if included_vars.belief_reward:
        beliefs_names = beliefs_names + ('nao offering rewards', )
    if included_vars.action_change_diff:
        goals_names = goals_names + ('change game difficulty', )
    if included_vars.goal_get_help:
        goals_names = goals_names + ('get help', )
    if included_vars.goal_reward:
        goals_names = goals_names + ('get reward', )
    if included_vars.action_skip:
        goals_names = goals_names + ('skip puzzle', )
    if included_vars.emotion_happy:
        emotions_names = emotions_names + ('happy/unhappy', )
    if included_vars.gp_challenged:
        gps_names = gps_names + ['challenged preference']
    beliefs, goals, emotions, biases, rpks, pks, gps, pts, gwk \
        = declare.declare_all_cognitive_variables(beliefs_names, goals_names, emotions_names, (), (), (),
                                                  initial_value=0, range_values=(-1, 1),
                                                  update_rate=included_vars.vars_update_rate,
                                                  bound_variables=included_vars.bound_variables,
                                                  incremental_variables=included_vars.incremental_variables,
                                                  incremental_var_slow=included_vars.incremental_var_slow)
    gps = declare.declare_1_type_of_slow_dyn_variables(slw_dyn.GeneralPreferences, gps_names, initial_value=1)
    pts = declare.declare_1_type_of_slow_dyn_variables(slw_dyn.PersonalityTraits, pts_names, initial_value=1)
    return beliefs, goals, emotions, biases, rpks, pks, gps, pts


def declare_decision_making_vars(beliefs, goals, included_vars):
    """ declares the variables of the decision-making module of the tom model

    Parameters
    ----------
    beliefs : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]
    goals : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal]
    included_vars : experimentNao.declare_model.included_elements.IncludedElements

    Returns
    -------
    Tuple[List[experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame], List[experimentNao.declare_model.modules.declare_decision_making.ActionChessGame]]
    """
    vars_descriptions = [['quit game', ['keep playing', 'quit game'], goals['quit game'], None, True]]
    if included_vars.action_change_diff:
        goal = goals['change game difficulty']
        vars_descriptions.append(['ask for easier game', ['do not ask', 'ask'], goal, None, False])
        vars_descriptions.append(['ask for more difficult game', ['do not ask', 'ask'],  goal, None, True])
    if included_vars.belief_nao_helping and included_vars.goal_get_help:
        vars_descriptions.append(['ask for help', ['do not ask', 'ask'], goals['get help'], beliefs['nao helping'], True])
    elif included_vars.goal_get_help:
        vars_descriptions.append(['ask for help', ['do not ask', 'ask'], goals['get help'], None, True])
    if included_vars.action_skip:
        vars_descriptions.append(['skip puzzle', ['do not skip', 'skip'],  goals['skip puzzle'], None, True])

    intentions, actions = [], []
    for description in vars_descriptions:
        intentions.append(declare_dm.IntentionChessGame(description[0], 0.5, description[2], belief=description[3],
                                                        verbal_terms=description[1],
                                                        larger_than_threshold=description[4]))
        actions.append(declare_dm.ActionChessGame(description[0], description[1]))
    return intentions, actions


def declare_perception_vars(rpk):
    """ declares the variables of the perception module of the tom model

    Parameters
    ----------
    rpk : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.RationallyPerceivedKnowledge]

    Returns
    -------
    Tuple[experimentNao.declare_model.modules.declare_perception_module.ChessRLD, experimentNao.declare_model.modules.declare_perception_module.ChessPerceivedData, experimentNao.declare_model.modules.declare_perception_module.ChessRationallyPerceivedKnowledge]
    """
    rld = declare_percept.ChessRLD('real life data for interaction with nao', int_data.ChessInteractionData())
    pd = declare_percept.ChessPerceivedData('perceived data for interaction with nao', int_data.ChessInteractionData())
    rpk_set = declare_percept.ChessRationallyPerceivedKnowledge('rationally perceived knowledge for interaction with nao',
                                                                int_data.ChessInteractionData(), rpk)
    return rld, pd, rpk_set
