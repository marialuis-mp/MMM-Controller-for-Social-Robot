from lib.tom_model.model_declaration_auxiliary.variables_declaration_aux import declare_1_type_of_fst_dyn_variables, \
    declare_all_cognitive_variables
from lib.tom_model.model_elements.variables import fst_dynamics_variables as fst_dyn, slow_dynamics_variables as slw_dyn
from lib.tom_model.model_elements.variables.fst_dynamics_variables import BoundMethod
from lib.tom_model.usage_example import declare_perception_module, declare_decision_making as declare_dm


def declare_all_variables():
    beliefs, goals, emotions, biases, rpk, perceived_knowledge, gps, pts = declare_cognitive_vars_very_simplified()
    # ** or, for a more tailored declaration, uncomment next line:
    # beliefs, goals, emotions, biases, perceived_knowledge, gps, pts = declare_cognitive_vars_simplified()
    # ** or, for an even more tailored declaration, uncomment next line:
    # beliefs, goals, emotions, biases, perceived_knowledge, gps, pts = declare_cognitive_vars_tailored()
    intentions, actions = declare_decision_making_vars(beliefs, goals)
    rld, pd, pk_set = declare_perception_vars(perceived_knowledge)

    return beliefs, goals, emotions, biases, rpk, perceived_knowledge, gps, pts, intentions, actions, rld, pd, pk_set


def declare_cognitive_vars_very_simplified():
    """ the most compact declaration, where you only need to specify the names of each variable, grouped by type.
    The downside is that all the variables will have the same initial value and range values. If you need to specify
    this, see bellow 'declare_cognitive_vars_simplified' or 'declare_cognitive'

    Returns
    -------

    """
    beliefs, goals, emotions, biases, rpks, pks, general_preferences, personality_traits, general_world_knowledge = \
        declare_all_cognitive_variables(names_beliefs=['there is cake', 'there is fruit', 'ate cake', 'ate fruit'],
                                        names_goals=['keep diet', 'eat cake', 'eat fruit'],
                                        names_emotions=['happy', 'guilty'],
                                        names_gps=['cake preference', 'fruit preference'],
                                        names_pts=['disciplined'],
                                        names_gwk=[],
                                        initial_value=0.3, range_values=(-1, 1), update_rate=1.0,
                                        bound_variables=BoundMethod.NONE, incremental_variables=False,
                                        incremental_var_slow=False)
    return beliefs, goals, emotions, biases, rpks, pks, general_preferences, personality_traits


def declare_cognitive_vars_simplified():
    """ compact declaration where you can define the initial value and ranges of each group of variables. However, you
    cannot set the initial values or other parameters of each variable independently. If you need to do so, check the
    example 'declare_cognitive_vars_tailored'

    Returns
    -------

    """
    names_beliefs = ['there is cake', 'there is fruit', 'ate cake', 'ate fruit']
    beliefs = declare_1_type_of_fst_dyn_variables(fst_dyn.Belief, names_beliefs, initial_value=0)
    biases = declare_1_type_of_fst_dyn_variables(fst_dyn.Bias, names_beliefs, initial_value=0)
    pks = declare_1_type_of_fst_dyn_variables(fst_dyn.RationallyPerceivedKnowledge, names_beliefs, initial_value=0)
    # Other variables
    goals = declare_1_type_of_fst_dyn_variables(fst_dyn.Goal, list_of_names=['keep diet', 'eat cake', 'eat fruit'],
                                                initial_value=0.2, range_values=(-1, 1))
    emotions = declare_1_type_of_fst_dyn_variables(fst_dyn.Emotion, list_of_names=['happy', 'guilty'],
                                                   initial_value=0.3, range_values=(-1, 1))
    general_preferences = declare_1_type_of_fst_dyn_variables(slw_dyn.GeneralPreferences,
                                                              list_of_names=['cake preference', 'fruit preference'],
                                                              initial_value=1)
    personality_traits = declare_1_type_of_fst_dyn_variables(slw_dyn.PersonalityTraits,
                                                             list_of_names=['disciplined'], initial_value=1)
    return beliefs, goals, emotions, biases, pks, general_preferences, personality_traits


def declare_cognitive_vars_tailored():
    """ completely tailored declaration, where you can specify the initial value and range values of each variable

    Returns
    -------
    Union[Tuple[Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal], Dict, Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias], Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge], Dict[str, lib.tom_model.model_elements.variables.slow_dynamics_variables.GeneralPreferences], Dict[str, lib.tom_model.model_elements.variables.slow_dynamics_variables.PersonalityTraits]], Tuple[Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal], Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias], Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge], Dict[str, lib.tom_model.model_elements.variables.slow_dynamics_variables.GeneralPreferences], Dict[str, lib.tom_model.model_elements.variables.slow_dynamics_variables.PersonalityTraits]]]
    """
    beliefs, pks, biases = dict(), dict(), dict()       # Declare the beliefs, perceived knowledge, and bias together
    for type_of_var in [[beliefs, fst_dyn.Belief], [pks, fst_dyn.RationallyPerceivedKnowledge], [biases, fst_dyn.Bias]]:
        for name in ['there is cake', 'there is fruit', 'ate cake', 'ate fruit']:
            type_of_var[0][name] = type_of_var[1](name, initial_value=0)

    goals = dict()
    for name in ['keep diet', 'eat cake', 'eat fruit']:       # choose the initial value and ranges that best suit you
        goals[name] = fst_dyn.Goal(name, initial_value=0.2, range_values=(-1, 1))

    emotions = dict()   # if choice of initial value is different for different variables, separate them
    emotions['happy'] = fst_dyn.Emotion(name, initial_value=0.3, range_values=(-1, 1))
    emotions['guilty'] = fst_dyn.Emotion(name, initial_value=0.4, range_values=(-1, 1))

    general_preferences = dict()
    for name in ['cake preference', 'fruit preference']:
        general_preferences[name] = slw_dyn.GeneralPreferences(name, initial_value=1)

    personality_traits = dict()
    for name in ['disciplined']:
        personality_traits[name] = slw_dyn.PersonalityTraits(name, initial_value=1)

    return beliefs, goals, emotions, biases, pks, general_preferences, personality_traits


def declare_decision_making_vars(beliefs, goals, ):
    vars_descriptions = [['eat cake', goals['eat cake'], beliefs['there is cake'], ['do not eat', 'eat'], 'cake'],
                         ['eat fruit', goals['eat fruit'], beliefs['there is fruit'], ['do not eat', 'eat'], 'fruit']]

    intentions, actions = [], []
    for description in vars_descriptions:
        intentions.append(declare_dm.IntentionEating(name=description[0], goal=description[1], belief=description[2],
                                                     verbal_terms=description[3], food=description[4]))
        actions.append(declare_dm.ActionEating(name=description[0], verbal_terms=description[3], food=description[4]))
    return intentions, actions


def declare_perception_vars(pk):
    rld = declare_perception_module.FoodRLD('real life data for eating', declare_perception_module.FoodData())
    pd = declare_perception_module.FoodPerceivedData('perceived data for eating', declare_perception_module.FoodData())
    pk_set = declare_perception_module.FoodPerceivedKnowledge('perceived knowledge set for eating',
                                                              declare_perception_module.FoodData(), pk)
    return rld, pd, pk_set
