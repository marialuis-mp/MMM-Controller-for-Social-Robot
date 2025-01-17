from lib.tom_model.model_elements.variables import fst_dynamics_variables as fst_dyn
from lib.tom_model.model_elements.linkage.scheduled_weight import ScheduledWeight


def add_several_influencers_w_sw(variable: fst_dyn.FastDynamicsVariable, influencers, boundary_values=None):
    """ add several influencers of 1 variable, each one with a Scheduled Weight. With scheduled weights, since it is not
     known how many weights there will be between two variables, the default scheduled weight is a list of two null
     weights: [0, 0].

    Parameters
    ----------
    variable : the variable to which the influencer will be added
    influencers : the list of influencers
    boundary_values : min and max values that the parameters of the weights that define the linkage between the
        influencer and variable can assume
    """
    if boundary_values is None:
        for influencer in influencers:
            variable.add_one_influencer(influencer, influencer_rules_or_weight=ScheduledWeight())
    else:
        for influencer in influencers:
            variable.add_one_influencer(influencer, influencer_rules_or_weight=ScheduledWeight(),
                                        inf_boundary_values=boundary_values)


def add_several_influencers_simple(variable: fst_dyn.FastDynamicsVariable, influencers, boundary_values=None):
    """ add several influencers of 1 variable, each one with a simple weight (float). It adds the variables with a
    default weight of 1.

    Parameters
    ----------
    variable : the variable to which the influencer will be added
    influencers : the list of influencers
    boundary_values : min and max values that the parameters of the linkage between the influencer and variable can assume
    """
    if boundary_values is None:
        for influencer in influencers:
            variable.add_one_influencer(influencer, influencer_rules_or_weight=1)
    else:
        for influencer in influencers:
            variable.add_one_influencer(influencer, influencer_rules_or_weight=1, inf_boundary_values=boundary_values)