from lib.tom_model.model_elements.variables import fst_dynamics_variables as fst_dyn, slow_dynamics_variables as slw_dyn


def declare_all_cognitive_variables(names_beliefs, names_goals, names_emotions, names_pts, names_gps, names_gwk,
                                    initial_value, range_values, update_rate, bound_variables, incremental_variables,
                                    incremental_var_slow):
    """ Useful to declare all the cognitive variables of the model when their initial value of range_values are the same.
    Otherwise, use the example in the folder 'usage_example' to see how to declare them seperately

    Parameters
    ----------
    names_beliefs : names of the beliefs
    names_goals : names of the goals
    names_emotions : names of the emotions
    names_pts : names of the personality traits
    names_gps : names of the general preferences
    names_gwk : names of the general world knowledge pieces
    initial_value : initial value of all the variables
    range_values :  tuple with minimum and maximum value that all the variables can take
    update_rate : the rate with which the new value is updated (see class CognitiveVariable for further explanation)
    bound_variables : whether vars are bounded using tanh (see class CognitiveVariable for further explanation)
    incremental_variables : weather the variable update is done by increment/decrementing the previous value or from
                           scratch.
    incremental_var_slow: similar to 'incremental_variables' but with a lower update rate

    Returns
    -------

    """
    # Declare the beliefs, perceived knowledge, and bias together
    beliefs, biases, rpks, pks = declare_beliefs_biases_and_pks(names_beliefs, initial_value, range_values,
                                                                bound_variables)
    # Declare other fast dynamics state variables
    goals = declare_1_type_of_fst_dyn_variables(fst_dyn.Goal, names_goals, initial_value, range_values,
                                                update_rate, bound_variables,
                                                incremental_variables, incremental_var_slow)
    emotions = declare_1_type_of_fst_dyn_variables(fst_dyn.Emotion, names_emotions, initial_value, range_values,
                                                   update_rate, bound_variables,
                                                   incremental_variables, incremental_var_slow)
    # Declare slow dynamics state variables
    general_world_knowledge = declare_1_type_of_slow_dyn_variables(slw_dyn.GeneralWorldKnowledge, names_gwk,
                                                                   initial_value, range_values)
    general_preferences = declare_1_type_of_slow_dyn_variables(slw_dyn.GeneralPreferences, names_gps, initial_value,
                                                               range_values)
    personality_traits = declare_1_type_of_slow_dyn_variables(slw_dyn.PersonalityTraits, names_pts, initial_value,
                                                              range_values)
    return beliefs, goals, emotions, biases, rpks, pks, general_preferences, personality_traits, general_world_knowledge


def declare_1_type_of_fst_dyn_variables(variables_type, list_of_names, initial_value=0, range_values=(-1, 1),
                                        update_rate=1, bound_variables=False, incremental_variables=False,
                                        incremental_var_slow=False):
    """ declare all fast dynamics state variables from one type when they have the same initial value and their allowed
    minimum and maximum values are the same

    Parameters
    ----------
    variables_type : Type of the variables (e.g., Belief, Goal, etc...)
    list_of_names : List with the identifying names of all the variables (one name per variable)
    initial_value : initial value of all the variables
    range_values :  tuple with minimum and maximum value that all the variables can take
    update_rate : the rate with which the new value is updated (see class CognitiveVariable for further explanation)
    bound_variables : whether vars are bounded using tanh (see class CognitiveVariable for further explanation)
    incremental_variables : weather the variable update is done by increment/decrementing the previous value or from
                           scratch.
    incremental_var_slow: similar to 'incremental_variables' but with a lower update rate

    Returns
    -------

    """
    variables_dict = dict()
    for name in list_of_names:
        variables_dict[name] = variables_type(name, initial_value=initial_value, range_values=range_values,
                                              update_rate=update_rate, bound_variable=bound_variables,
                                              incremental_variable=incremental_variables,
                                              incremental_var_slow=incremental_var_slow)
    return variables_dict


def declare_1_type_of_slow_dyn_variables(variables_type, list_of_names, initial_value=0, range_values=(-1, 1)):
    """ declare all slow dynamics state variables from one type when they have the same initial value and their allowed
    minimum and maximum values are the same

    Parameters
    ----------
    variables_type : Type of the variables (e.g., Belief, Goal, etc...)
    list_of_names : List with the identifying names of all the variables (one name per variable)
    initial_value : initial value of all the variables
    range_values :  tuple with minimum and maximum value that all the variables can take

    Returns
    -------

    """
    variables_dict = dict()
    for name in list_of_names:
        variables_dict[name] = variables_type(name, initial_value=initial_value, range_values=range_values)
    return variables_dict


def declare_beliefs_biases_and_pks(list_of_beliefs_names, initial_value=0, range_values=(-1, 1), bound_variables=False):
    beliefs = declare_1_type_of_fst_dyn_variables(fst_dyn.Belief, list_of_beliefs_names, initial_value,
                                                  range_values, bound_variables=bound_variables)
    biases = declare_1_type_of_fst_dyn_variables(fst_dyn.Bias, list_of_beliefs_names, initial_value, range_values,
                                                 bound_variables=bound_variables)
    rpks = declare_1_type_of_fst_dyn_variables(fst_dyn.RationallyPerceivedKnowledge, list_of_beliefs_names,
                                               initial_value, range_values)
    pks = declare_1_type_of_fst_dyn_variables(fst_dyn.PerceivedKnowledge, list_of_beliefs_names, initial_value,
                                              range_values)
    return beliefs, biases, rpks, pks
