from enum import Enum

# from tensorflow.python.autograph.core.converter import Base
from lib.tom_model.model_elements.variables.fst_dynamics_variables import BoundMethod

from experimentNao.declare_model.included_elements import IncludedElements


class ModelConfigs(Enum):
    """ Different configurations of the model

    """
    DEFAULT = 1
    # Perception variations
    PER_LIN = 2
    # Cognition variations - Scheduled weights
    COG_SW = 3   # scheduled weights: all instead of just beliefs
    COG_NO_SW = 4   # scheduled weights: none at all
    # Cognition variations - Simple model
    SIMPLEST = 5
    # Extra bias
    DEFAULT_BIAS = 6
    SIMPLEST_W_BIAS = 7
    # EXTRA SIMPLE
    SIMPLEST_NO_SW_BIAS = 8
    NO_SW_BIAS = 9
    # SLOW INCR
    SIMPLEST_W_BIAS_SLOW = 10
    SIMPLEST_NO_SW_BIAS_SLOW = 11


def get_model_configuration(model_config: ModelConfigs, incremental=False):
    """ returns the object that contains the information about which elements should be included in the model depending
    on the model configuration model_config passed as an argument, and whether the incremental assumption is taken.

    Parameters
    ----------
    model_config : experimentNao.model_ID.configs.model_configs.ModelConfigs
    incremental : bool

    Returns
    -------
    experimentNao.declare_model.included_elements.IncludedElements
    """
    if model_config == ModelConfigs.DEFAULT:
        included_elements = get_experiment_incl_elements(incremental_variables=incremental)
    elif model_config == ModelConfigs.PER_LIN:
        included_elements = get_experiment_incl_elements(incremental_variables=incremental, nonlinear_perception=False)
    elif model_config == ModelConfigs.COG_SW:
        included_elements = get_experiment_incl_elements(incremental_variables=incremental, all_scheduled_weights=True)
    elif model_config == ModelConfigs.COG_NO_SW:
        included_elements = get_experiment_incl_elements(incremental_variables=incremental, all_scheduled_weights=False,
                                                         scheduled_weights_for_diff=False, scheduled_weights_for_reward=False)
    elif model_config == ModelConfigs.SIMPLEST:
        included_elements = get_experiment_incl_elements(incremental_variables=incremental, goal_get_help=False,
                                                         action_change_diff=False)
    elif model_config == ModelConfigs.DEFAULT_BIAS:
        included_elements = get_experiment_incl_elements(incremental_variables=incremental, bias_bored_on_diff=True)
    elif model_config == ModelConfigs.SIMPLEST_W_BIAS:
        included_elements = get_experiment_incl_elements(incremental_variables=incremental, bias_bored_on_diff=True,
                                                         goal_get_help=False, action_change_diff=False)
    elif model_config == ModelConfigs.SIMPLEST_NO_SW_BIAS:
        included_elements = get_experiment_incl_elements(incremental_variables=incremental, bias_bored_on_diff=True,
                                                         goal_get_help=False, action_change_diff=False,
                                                         all_scheduled_weights=False, scheduled_weights_for_diff=False,
                                                         scheduled_weights_for_reward=False)
    elif model_config == ModelConfigs.NO_SW_BIAS:
        included_elements = get_experiment_incl_elements(incremental_variables=incremental, bias_bored_on_diff=True,
                                                         all_scheduled_weights=False, scheduled_weights_for_diff=False,
                                                         scheduled_weights_for_reward=False)
    elif model_config == ModelConfigs.SIMPLEST_W_BIAS_SLOW:
        included_elements = get_experiment_incl_elements(incremental_variables=incremental, bias_bored_on_diff=True,
                                                         goal_get_help=False, action_change_diff=False,
                                                         incremental_var_slow=True)
    elif model_config == ModelConfigs.SIMPLEST_NO_SW_BIAS_SLOW:
        included_elements = get_experiment_incl_elements(incremental_variables=incremental, bias_bored_on_diff=True,
                                                         goal_get_help=False, action_change_diff=False,
                                                         all_scheduled_weights=False, scheduled_weights_for_diff=False,
                                                         scheduled_weights_for_reward=False, incremental_var_slow=True)
    else:
        raise ValueError('model_config is not any pre-defined ModelConfig')
    return included_elements


def get_experiment_incl_elements(all_scheduled_weights=False, scheduled_weights_for_diff=True,
                                 scheduled_weights_for_reward=True, emotion_self_influences=False,
                                 nonlinear_perception=True, simplified_perception=True,
                                 goal_get_help=True, action_change_diff=True, bias_bored_on_diff=False,
                                 incremental_variables=False, incremental_var_slow=False,
                                 bound_variables=BoundMethod.NONE, vars_update_rate=1.0):
    """ Returns the included elements of the model, according to the input arguments, but constrained by what is allowed
    in the experiment with the participants (i.e., only certain configurations of included elements are allowed,
    according to the design of the experiment). Moreover, the default values of the arguments of the function are
    the default elements chosen in the design of the experiment.

    Parameters
    ----------
    all_scheduled_weights : bool
    scheduled_weights_for_diff : bool
    scheduled_weights_for_reward : bool
    emotion_self_influences : bool
    nonlinear_perception : bool
    simplified_perception : bool
    goal_get_help : bool
    action_change_diff : bool
    bias_bored_on_diff : bool
    incremental_variables : bool
    incremental_var_slow : bool
    bound_variables : lib.tom_model.model_elements.variables.fst_dynamics_variables.BoundMethod
    vars_update_rate : float

    Returns
    -------

    """
    return IncludedElements(belief_made_progress=False, belief_nao_helping=False, belief_reward=True,
                            belief_reward_hidden=True, goal_reward=False, goal_get_help=goal_get_help,
                            emotion_happy=False, action_skip=True, action_change_diff=action_change_diff,
                            gp_challenged=False, switch_get_help_influencer=False,
                            inf_nao_hinders_on_get_help=False, inf_nao_hinders_on_frustrated=False,
                            inf_difficulty_on_skip=True, inf_difficulty_on_frustrated=True,
                            inf_made_progress_on_bored=False, inf_bored_on_skip=False,
                            all_scheduled_weights=all_scheduled_weights, scheduled_weights_for_diff=scheduled_weights_for_diff,
                            scheduled_weights_for_reward=scheduled_weights_for_reward, bias_bored_on_diff=bias_bored_on_diff,
                            emotion_self_influences=emotion_self_influences,
                            nonlinear_perception=nonlinear_perception, simplified_perception=simplified_perception,
                            bound_variables=bound_variables, constrained_bias_weight=False,
                            vars_update_rate=vars_update_rate,
                            incremental_variables=incremental_variables, incremental_var_slow=incremental_var_slow)
