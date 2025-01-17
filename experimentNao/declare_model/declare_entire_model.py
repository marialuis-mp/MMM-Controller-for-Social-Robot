from experimentNao.declare_model import declare_variables
from experimentNao.declare_model import included_elements
from experimentNao.declare_model.modules import declare_perception_module, declare_cognitive_module as declare_cognition, \
    declare_decision_making
from experimentNao.model_ID.configs import model_configs
from experimentNao.model_ID.data_processing import excel_data_processing as edp
from lib.tom_model.model_structure import perception_module, decision_making_module, tom_model


def get_model_from_config(overall_id_config, max_values_rld):
    """ declares and returns the tom model, according to the "overall_id_config".

    Parameters
    ----------
    overall_id_config : experimentNao.model_ID.configs.overall_config.IDConfig
    max_values_rld : Dict[str, int]

    Returns
    -------
    Union[experimentNao.declare_model.declare_entire_model.ToMModelChess, experimentNao.declare_model.declare_entire_model.ToMModelChessSimpleDyn]
    """
    included_elements = model_configs.get_model_configuration(overall_id_config.model_config,
                                                              overall_id_config.incremental)
    tom_model_ = declare_model(included_elements, max_values_rld, overall_id_config)
    return tom_model_


def get_normalization_values_of_rld(file, from_id=None):
    """ gets the values that will be used to normalise the real life data of each participant

    Parameters
    ----------
    file : Union[None, pandas.io.excel._base.ExcelFile]
    from_id : Union[bool, None]

    Returns
    -------
    Union[Dict[str, int], Dict[str, float]]
    """
    if file is None:
        return declare_perception_module.get_default_max_values()
    return edp.get_normalization_values_of_rld_from_id_file(file) if from_id \
        else edp.get_normalization_values_of_rld_from_participant_file(file)


def declare_model(included_vars: included_elements.IncludedElements, max_values_rld, overall_id_config):
    """  declares and returns the tom model, according to the object that contains the information about which elements
    should be included in the model "included_vars".

    Parameters
    ----------
    included_vars : experimentNao.declare_model.included_elements.IncludedElements
    max_values_rld : Union[Dict[str, int], Dict[str, float], Dict[str, float], Dict[str, float], Dict[str, float], Dict[str, float]]
    overall_id_config : experimentNao.model_ID.configs.overall_config.IDConfig

    Returns
    -------
    Union[experimentNao.declare_model.declare_entire_model.ToMModelChessSimpleDyn, experimentNao.declare_model.declare_entire_model.ToMModelChess]
    """
    time_steps4convergence = 2
    # All vars
    beliefs, goals, emotions, biases, rpk, pk, gps, pts, intentions, actions, rld, pd, rpk_set \
        = declare_variables.declare_all_variables(included_vars)

    # Cognitive
    beliefs, goals, emotions, biases, rpk, pk, gps, pts \
        = declare_cognition.declare_all_linkages(beliefs, goals, emotions, biases, rpk, pk, gps, pts, included_vars,
                                                 simplified_dynamics=overall_id_config.simple_dynamics)
    if not overall_id_config.simple_dynamics:
        cognitive = declare_cognition.CognitiveModuleChess(beliefs, goals, emotions, biases, pk=None, gps=gps, pts=pts)
    else:
        cognitive = declare_cognition.CognitiveModuleChess(beliefs, goals, emotions, biases, pk=pk, gps=gps, pts=pts)

    # Decision
    intention_selector = declare_decision_making.HumanIntentionSelector(beliefs, goals, intentions)
    action_selector = declare_decision_making.HumanActionSelector(intentions, actions)
    decision_making = decision_making_module.DecisionMakingModule(intention_selector, action_selector)

    # Perception
    perceptual_access_process = declare_perception_module.HumanPerceptualAccess(rld, pd)
    rational_reasoning_process = declare_perception_module.HumanRationalReasoning(pd, rpk_set, included_vars, max_values_rld)
    perception = perception_module.PerceptionModule(perceptual_access_process, rational_reasoning_process)

    if not overall_id_config.simple_dynamics:
        model = ToMModelChess(cognitive, decision_making, perception, time_steps4convergence)
    else:
        model = ToMModelChessSimpleDyn(cognitive, decision_making, perception, time_steps4convergence)
    return model


class ToMModelChess(tom_model.TomModel):
    def update_entire_model_in_1_go(self, compute_optimal_action):
        self.perception_module.compute_and_update_module_in_1_go()
        for k in range(self.time_steps4convergence):
            self.cognitive_module.compute_and_update_module()       # the module is the CognitiveModuleChess
        if compute_optimal_action:
            self.decision_making_module.compute_and_update_module_in_1_go()


class ToMModelChessSimpleDyn(tom_model.TomModel):
    def update_entire_model_in_1_go(self, compute_optimal_action):
        self.perception_module.compute_and_update_module_in_1_go()
        for pk in self.cognitive_module.pk:
            pk.compute_variable_value()
            pk.update_value()
        for k in range(self.time_steps4convergence):
            self.cognitive_module.compute_and_update_module()       # the module is the CognitiveModuleChess
        if compute_optimal_action:
            self.decision_making_module.compute_and_update_module_in_1_go()
