from lib.tom_model.model_declaration_auxiliary.linkages_declaration_aux import add_several_influencers_w_sw, \
    add_several_influencers_simple
from lib.tom_model.model_elements.linkage.scheduled_weight import ScheduledWeight


def declare_all_linkages(beliefs, goals, emotions, biases, rpk, pk, gps, pts):
    """ declares the connections (linkages) that are part of the cognitive module. Several ways of declaring the
    linkages are illustrated in this file

    Returns
    -------

    """
    beliefs = declare_beliefs_influencers(beliefs, rpk, pk, biases)
    goals = declare_goals_influencers(beliefs, goals, emotions, gps, pts)
    emotions = declare_emotions_influencers(beliefs, goals, emotions, pts, gps)
    biases = declare_biases_influencers(biases, emotions)
    return beliefs, goals, emotions, biases, pk, gps, pts


def declare_beliefs_influencers(beliefs, rpk, pk, biases):
    bv = (0, 1)  # boundary values of the linkages (not of the variables)
    # It is possible to add several influencers to one variable
    # The default weight is 1
    for name in ['there is cake', 'there is fruit', 'ate cake', 'ate fruit']:    # beliefs should be influenced by corresponding pk and bias only
        add_several_influencers_simple(pk[name], (rpk[name], biases[name]), boundary_values=bv)
        add_several_influencers_simple(beliefs[name], (pk[name], ), boundary_values=bv)
    return beliefs


def declare_goals_influencers(beliefs, goals, emotions, general_preferences, personality_traits):
    # Example: adding the linkages of the goals with schedule weights instead
    # it is possible to add 1 or more influencers
    add_several_influencers_w_sw(goals['keep diet'], (personality_traits['disciplined'], ))
    add_several_influencers_w_sw(goals['eat fruit'], (beliefs['there is fruit'], emotions['guilty'],
                                                      general_preferences['fruit preference']))
    add_several_influencers_w_sw(goals['eat cake'], (beliefs['there is cake'],
                                                     emotions['happy']))
    #   With scheduled weights, since it is not known how many weights there will be between two variables, the default
    # scheduled weight is a list of two: [0, 0]
    #   Thus, it is necessary to add the weights between the variables
    for goal_name in ['keep diet', 'eat fruit', 'eat cake']:
        for influencer in goals[goal_name].influencers:
            influencer.influencer_linkage.weights = [0.5, 0.5]
    return goals


def declare_emotions_influencers(beliefs, goals, emotions, personality_traits, general_preferences):
    # When we want to add influencers 1 by 1 (for example, if they have different characteristics)
    emotions['guilty'].add_one_influencer(beliefs['ate fruit'])         # no scheduled weight
    emotions['guilty'].add_one_influencer(beliefs['ate cake'],          # with scheduled weight - & set value of weights
                                          influencer_rules_or_weight=ScheduledWeight(weights=[0.9, 0.3]))
    emotions['happy'].add_one_influencer(beliefs['ate cake'],
                                         influencer_rules_or_weight=0.4,  # no scheduled weight - & set value of linkage
                                         influencer_side_linkage=goals['eat cake'])
    emotions['happy'].add_one_influencer(beliefs['ate cake'],
                                         influencer_side_linkage=general_preferences['cake preference'])
    return emotions


def declare_biases_influencers(biases, emotions):
    biases['there is cake'].add_one_influencer(emotions['happy'], influencer_rules_or_weight=1)
    return biases
