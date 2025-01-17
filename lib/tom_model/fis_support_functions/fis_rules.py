from skfuzzy import control as ctrl
import lib.tom_model.fis_support_functions.fis_membership_functions as msf
from lib.tom_model import config
import numpy as np


def add_1_set_rules(variable, terms_cons, influencer, terms_ant, about_same_ent=False, weight=None):
    """ Declares the rules between a variable and an influencer, and adds the influencer (with the rules) to the
    cognitive variable. The rules are added in terms of 'if influencer is X then variable is Y', in which X is one of
    terms_cons and Y is the corresponding terms_ant. The number of rules declared in this set is equal to the length
    of both terms_cons and terms_ant.

    Parameters
    ----------
    variable : lib.elements.variables.fst_dynamics_variables.FastDynamicsElement
        the consequent in the IF rule (i.e., the variable that is influenced); the variable to which the set and influencer are added to
    terms_cons : list[str]
        the n verbal terms that are associated with 'variable'
    influencer : Union[lib.model_elements.variables.fst_dynamics_variables.FastDynamicsElement, lib.model_elements.variables.slow_dynamics_variables.SlowDynamicsElement]
        the antecedent in the IF rule (i.e., the variable that influences)
    terms_ant : list[str]
        the n verbal terms that are associated with 'consequent'
    about_same_ent : bool
        should be True if both variables in the rule are about the same entity
    weight : Union[None, float]
        defines the weight of the rule after the rule is fired

    Returns
    -------
    Union[lib.model_elements.variables.fst_dynamics_variables.Goal, lib.model_elements.variables.fst_dynamics_variables.Belief, lib.model_elements.variables.fst_dynamics_variables.Emotions, lib.model_elements.variables.fst_dynamics_variables.Bias]
    """
    # A) Assertations
    if about_same_ent:
        assert variable.object_of_variable == influencer.object_of_variable
    if len(terms_ant) != len(terms_cons):
        raise ValueError("Number of terms of antecedent differs from number of terms of consequent.")
    # B) Create set of rules
    rules = RuleSet()
    for i in range(len(terms_ant)):
        if weight is None:
            rules.add(ctrl.Rule(influencer.antecedent[terms_ant[i]], variable.consequent[terms_cons[i]]))
        else:
            rules.add(ctrl.Rule(influencer.antecedent[terms_ant[i]], variable.consequent[terms_cons[i]] % weight))
    # C) Add influencer and set of rules to variable
    variable.add_one_influencer(influencer, rules)
    return variable


def add_1_group_complex_rules(variable, var_terms, terms_matrix, influencer, inf_term, side_linkage, side_linkage_terms,
                              about_same_var=False):
    """ Declares the complex rules between a variable i, an influencer j and a 3rd variable k, and adds the influencer j
    to the cognitive variable i. The rules are added in terms of 'if influencer is Y and side-linkage is Z, then
    variable is X', in which Y is one of terms_cons, Z is one of side_linkage_terms, and X is the corresponding
    var_terms (according to terms_matrix). The number of rules declared in this set is equal to the product between the
    length of inf_term, and the length of side_linkage_terms.

    Parameters
    ----------
    variable : lib.elements.variables.fst_dynamics_variables.Emotions
        the consequent in the IF rule (i.e., the variable that is influenced); the variable to which the set and influencer are added to
    var_terms : experiments2D.declare_system.declare_fuzzy_system.VerbalTerms
        the verbal terms associated with the variable
    terms_matrix : list[list[int]]
        matrix that contains n (number of influencer terms) arrays of dimensions m (number of side-linkage terms). Each
        matrix element {i,j} (which is an integer) defines which term of 'var_terms' is the consequent in the rule
        that has as antecedents the i-th verbal term of influencer and the j-th term of side-linkage.
    influencer : lib.elements.variables.fst_dynamics_variables.Belief
        the antecedent in the IF rule (i.e., the variable that influences). It is also the variable that is added as an
        influencer of 'variable'.
    inf_term : list[str]
        the n verbal terms associated with 'influencer'
    side_linkage : lib.elements.variables.slow_dynamics_variables.GeneralPreferences
        the second variable that influences the influence of 'influencer' on 'variable'
    side_linkage_terms :list[str]
        the m verbal terms associated with 'side-linkage'
    about_same_var : bool
        should be True if both variables in the rule are about the same entity

    Returns
    -------
    Union[lib.model_elements.variables.fst_dynamics_variables.Emotions, None]
    """
    # A) Assertations
    if about_same_var:
        assert variable.object_of_variable == influencer.object_of_variable
        assert variable.object_of_variable == side_linkage.object_of_variable
    assert len(terms_matrix) == len(inf_term)
    # B) For each value of the influencer Y, declare a set of rules 'If inf is Y and side-linkage is Z, then var is X'
    #    for the combinations of {X,Z} and fixed Y
    rules = RuleSet()
    for j in range(len(inf_term)):
        this_var_terms = var_terms.select_verbal_terms(terms_matrix[j])
        if len(side_linkage_terms) != len(this_var_terms):   # Make sure number of terms of var is number of terms of SL
            raise ValueError("Number of terms of antecedent differs from number of terms of consequent.")
        for i in range(len(this_var_terms)):
            rules.add(ctrl.Rule(influencer.antecedent[inf_term[j]] & side_linkage.antecedent[side_linkage_terms[i]],
                                variable.consequent[this_var_terms[i]]))
    # C) Add influencer and set of rules to variable
    variable.add_one_influencer(influencer, rules, side_linkage)
    return variable


def declare_1_composed_rule(variable, terms_cons, influencers, terms_ant, about_same_var=False, weight=1):
    """

    Parameters
    ----------
    variable : lib.elements.variables.fst_dynamics_variables.Goal
    terms_cons : list[str]
    influencers : list[lib.elements.variables.fst_dynamics_variables.Belief]
    terms_ant : list[list[str]]
    about_same_var : bool
    weight : int

    Returns
    -------
    lib.elements.variables.fst_dynamics_variables.Goal
    """
    assert len(terms_ant) == len(influencers)  # Confirm: number of influencers = the number of groups of terms
    for i in range(len(influencers)):
        if about_same_var:
            assert variable.object_of_variable == influencers[i].object_of_variable
        assert len(terms_ant[i]) == len(terms_cons)
    rules = RuleSet()
    for i in range(len(terms_ant[0])):
        # weight = weight / len(influencers)
        if len(influencers) == 1:
            rules.add(ctrl.Rule(influencers[0].antecedent[terms_ant[0][i]],
                                variable.consequent[terms_cons[i]] % weight))
        if len(influencers) == 2:

            rules.add(ctrl.Rule(influencers[0].antecedent[terms_ant[0][i]] &
                                influencers[1].antecedent[terms_ant[1][i]],
                                variable.consequent[terms_cons[i]] % weight))
        elif len(influencers) == 3:
            rules.add(ctrl.Rule(influencers[0].antecedent[terms_ant[0][i]] &
                                influencers[1].antecedent[terms_ant[1][i]] &
                                influencers[2].antecedent[terms_ant[2][i]],
                                variable.consequent[terms_cons[i]] % weight))
    for i in range(len(influencers)):
        variable.add_one_influencer(influencers[i], rules)
    return variable


def declare_antecedent(variable_name, terms, value_range, mf_type):
    antecedent = ctrl.Antecedent(np.arange(value_range[0], value_range[1], config.STEP), variable_name)
    membership_functions = msf.create_membership_functions(terms, value_range, mf_type)
    msf.attribute_membership_functions(antecedent, terms, membership_functions, mf_type)
    return antecedent


def declare_consequent(variable_name, terms, value_range, mf_type):
    if mf_type == 'default':
        dfzz_method = 'centroid'
    elif mf_type == 'binary':
        dfzz_method = 'mom'
    else:
        dfzz_method = 'centroid'
    consequent = ctrl.Consequent(np.arange(value_range[0], value_range[1], config.STEP), variable_name,
                                 defuzzify_method=dfzz_method)
    membership_functions = msf.create_membership_functions(terms, value_range, mf_type)
    msf.attribute_membership_functions(consequent, terms, membership_functions, mf_type)
    return consequent


def declare_antecedent_and_consequent(variable_name, terms, value_range, mf_type):
    consequent = declare_consequent(variable_name, terms, value_range, mf_type)
    antecedent = declare_antecedent(variable_name, terms, value_range, mf_type)
    return consequent, antecedent


class RuleSet:
    def __init__(self, initial_rules=[]):
        self.rules = []
        for ele in initial_rules:
            self.add(ele)

    def add(self, new_rule):
        if isinstance(new_rule, ctrl.Rule):
            self.rules.append(new_rule)
        else:
            raise TypeError("New rules must be of type of rule, not ", type(new_rule))

    def __add__(self, other):
        for ele in other.rules:
            self.add(ele)
        return self
