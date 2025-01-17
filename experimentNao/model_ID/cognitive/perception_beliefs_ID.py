from lib.tom_model.model_elements.variables.fst_dynamics_variables import Bias


def initialize_params_of_perception(percept_mdl, belief, random):
    """ Initializes all the parameters of the perception module associated with the "belief".

    Parameters
    ----------
    percept_mdl : lib.tom_model.model_structure.perception_module.PerceptionModule
    belief : Union[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]
    random : random.Random

    Returns
    -------
    List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]
    """
    corresponding_pk = next((pk for pk in percept_mdl.perceived_knowledge.knowledge if pk.name == belief.name))
    return percept_mdl.rational_reasoning.initialize_parameters_of_1_output(corresponding_pk, random)


def set_params_of_perception(percept_mdl, belief, parameters, parameters_counter):
    """ Sets the values of the parameters of the perception module associated with the "belief". The values come from
    the list "parameters", starting from parameters_counter until (parameters_counter+n_params_of_output-1).

    Parameters
    ----------
    percept_mdl : lib.tom_model.model_structure.perception_module.PerceptionModule
    belief : Union[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]
    parameters : List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]
    parameters_counter : int

    Returns
    -------
    int
    """
    corresponding_pk = next((pk for pk in percept_mdl.perceived_knowledge.knowledge if pk.name == belief.name))
    perceived_data, output_number, function = percept_mdl.rational_reasoning.get_output_info(corresponding_pk)
    n_params_of_output = percept_mdl.rational_reasoning.number_of_parameters[output_number]
    paramts = parameters[parameters_counter:parameters_counter+n_params_of_output]
    # paramts = parameters[-(percept_mdl.rational_reasoning.number_of_parameters[output_number]):]    # get last N params - why?
    percept_mdl.rational_reasoning.set_parameters_of_1_output(corresponding_pk, paramts)
    return n_params_of_output


def pre_process_belief_influencer(belief, perception_module, step):
    """ updates the values of the influencers of one belief (its influencing biases and perceived knowledge)

    Parameters
    ----------
    belief : lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief
    perception_module : lib.tom_model.model_structure.perception_module.PerceptionModule
    step : int
    """
    perception_module.perceptual_access.inputs.data = perception_module.perceptual_access.inputs.sequence_of_inputs[step]
    corresponding_pk = next((pk for pk in perception_module.perceived_knowledge.knowledge if pk.name == belief.name))
    compute_only_one_output_of_perception_module(perception_module, corresponding_pk)
    for inf in belief.influencers:
        if isinstance(inf.influencer_variable, Bias):
            for inf_of_bias in inf.influencer_variable.influencers:  # fill in the values of influencers of the bias
                inf_of_bias.influencer_variable.value = inf_of_bias.influencer_variable.values[step]
            inf.influencer_variable.compute_variable_value_fcm()
            inf.influencer_variable.update_value()


def compute_only_one_output_of_perception_module(perception_module, output):
    """ computes and updates one output of the perception module

    Parameters
    ----------
    perception_module : lib.tom_model.model_structure.perception_module.PerceptionModule
    output :
    """
    perception_module.perceptual_access.compute_new_value()
    perception_module.perceptual_access.update_value()
    # compute only the necessary output
    perception_module.rational_reasoning.run_rational_reasoning_1_output(output)
    output.update_value()
