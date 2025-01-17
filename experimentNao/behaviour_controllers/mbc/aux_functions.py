def print_values_of_computed_variables(tom_model):
    """ prints the values of computed variables of the tom model

    Parameters
    ----------
    tom_model : experimentNao.declare_model.declare_entire_model.ToMModelChessSimpleDyn
    """
    print_some_vars(get_all_fast_dyn_vars(tom_model))


def print_some_vars(some_vars):
    """ prints the type, name and value of some variables 'some_vars'

    Parameters
    ----------
    some_vars : Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.RationallyPerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.RationallyPerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias]
    """
    for var in some_vars:
        print('\t {}. - {}: {}'.format(str(type(var).__name__)[0:4], var.name, var.values))


def get_all_fast_dyn_vars(tom_model):
    """ returns all the rationally perceived knowledge, beliefs, goal, emotions, and biases

    Parameters
    ----------
    tom_model : experimentNao.declare_model.declare_entire_model.ToMModelChessSimpleDyn

    Returns
    -------
    Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.RationallyPerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.RationallyPerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias]
    """
    return get_rpks_of_model(tom_model) + tom_model.cognitive_module.state_vars + tom_model.cognitive_module.get_biases()


def get_rpks_of_model(tom_model):
    """ returns all the pieces of rationally perceived knowledge

    Parameters
    ----------
    tom_model : experimentNao.declare_model.declare_entire_model.ToMModelChessSimpleDyn

    Returns
    -------
    Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.RationallyPerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.RationallyPerceivedKnowledge]
    """
    return tom_model.perception_module.rational_reasoning.get_pks()
