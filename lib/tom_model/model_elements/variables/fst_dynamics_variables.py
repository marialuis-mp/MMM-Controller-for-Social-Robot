import copy
from abc import ABCMeta
from enum import Enum

import deprecation
import numpy
from skfuzzy import control as ctrl

import lib.tom_model.model_elements.variables.perception_variables
from lib.tom_model.model_elements.linkage import influencer
from lib.tom_model.model_elements.linkage.scheduled_weight import ScheduledWeight
from lib.tom_model.model_elements.variables import slow_dynamics_variables as slow_dyn, cognitive_variables
from lib.tom_model.fis_support_functions import fis_rules as rules
from lib.tom_model import config


class FastDynamicsVariable(cognitive_variables.CognitiveVariable):
    __metaclass__ = ABCMeta

    def __init__(self, name, initial_value=0, initial_influencers=tuple(), range_values=(-1, 1), verbal_terms=tuple(),
                 mf_type='default', update_rate=1, bound_variable=None, incremental_variable=False,
                 incremental_var_slow=False):
        super().__init__(name, initial_value, range_values, verbal_terms, mf_type, update_rate)
        self.influencers = []  # flexible constructor: allows to add influencers in constructor, or later on
        self.influencers_types = []
        for new_inf in initial_influencers:
            self.add_one_influencer(new_inf)
        if config.FRAMEWORK == 'FIS':
            self.terms = verbal_terms
            [self.consequent, self.antecedent] = rules.declare_antecedent_and_consequent(self.name, verbal_terms,
                                                                                         range_values, mf_type)
            self.var_fis = None
            self.control_system = []
        elif config.FRAMEWORK == 'FCM':
            bound_variable = BoundMethod.NONE if bound_variable is None else bound_variable
            assert isinstance(bound_variable, BoundMethod)
            self.bound = bound_variable     # bound output of compute next value with hyperbolic tangent
            self.incremental_variable = incremental_variable
            # self.incremental_value = 1.0 if self.bound else 0.9  # if var not bounded -> inc_value<1 to ensure stability
            self.incremental_value = 1.0 if self.bound is not BoundMethod.NONE else 0.9  # if var not bounded -> inc_value<1 to ensure stability
            if incremental_var_slow:
                self.incremental_value = 0.8

    def is_influencer(self, influencer_):
        return type(influencer_) in self.influencers_types

    def compute_variable_value(self):
        if config.FRAMEWORK == 'FIS':
            self.compute_variable_value_fis()
        elif config.FRAMEWORK == 'FCM':
            self.compute_variable_value_fcm()

    def compute_variable_value_fis(self):
        assert config.FRAMEWORK == 'FIS'
        var_fis = ctrl.ControlSystemSimulation(self.control_system)
        for inf in self.influencers:
            var_fis.input[inf.influencer_variable.name] = inf.influencer_variable.value
            if hasattr(inf, 'side_linkage'):
                var_fis.input[inf.side_linkage.name] = inf.side_linkage.value
        var_fis.compute()
        self.next_value = var_fis.output[self.name]
        # if isinstance(var, fast_dyn.Goal):
        #     var.consequent.view(sim=var_fis)
        self.set_var_fis(var_fis)

    def compute_variable_value_fcm(self):
        assert config.FRAMEWORK == 'FCM'
        value = 0
        if self.incremental_variable:
            value += self.incremental_value * self.value
        for inf in self.influencers:
            if isinstance(inf.influencer_linkage, ScheduledWeight):
                weight, i = inf.influencer_linkage.get_active_weight(inf.influencer_variable.value)
            else:
                weight = inf.influencer_linkage
            if not inf.has_side_linkage:
                value += inf.influencer_variable.value * weight
            else:
                value += inf.influencer_variable.value * weight * inf.side_linkage.value
        self.next_value = value
        if self.bound == BoundMethod.TANH:
            self.next_value = numpy.tanh(self.next_value)
        elif self.bound == BoundMethod.CLIP:
            self.next_value = min(max(self.next_value, self.minimum_value), self.maximum_value)

    def define_fis_control_system(self):
        set_of_rules = []
        for ele in self.influencers:
            one_influencer_rules = ele.influencer_linkage.rules
            for rule in one_influencer_rules:
                set_of_rules.append(rule)
        self.control_system = ctrl.ControlSystem(set_of_rules)

    def set_var_fis(self, var_fis):
        self.var_fis = var_fis

    def add_one_influencer(self, new_influencer, influencer_rules_or_weight=None, influencer_side_linkage=None,
                           inf_boundary_values=(-1, 1)):
        # 1. Check if new_influencer is allowed
        if not self.is_influencer(new_influencer):
            raise TypeError('Attempt to add influencer to variable ', self.name, ' failed. Influencer is of type ',
                            type(new_influencer), ' but only types ', self.influencers_types, 'are allowed. ')
        # 2a. Add influencer with rules or weights
        if cognitive_variables.is_pair_variable_value((new_influencer, influencer_rules_or_weight)):
            try:    # check whether this influencer is already an influencer of self
                inf = next(inf for inf in self.influencers if inf.influencer_variable == new_influencer)
                inf.add_more_rules(influencer_rules_or_weight)      # If so, add more rules to this influencer
            except StopIteration:                                   # If not, add it as a new influencer
                if influencer_side_linkage is None:
                    self.influencers.append(influencer.Influencer(new_influencer, influencer_rules_or_weight,
                                                                  boundary_values=inf_boundary_values))
                else:
                    self.influencers.append(influencer.Influencer(new_influencer, influencer_rules_or_weight, True,
                                                                  influencer_side_linkage, inf_boundary_values))
            finally:
                pass
        # 2b. Add influencer without rules or weights
        elif influencer_rules_or_weight is None:
            self.influencers.append(influencer.Influencer(new_influencer, 0, boundary_values=inf_boundary_values))
        else:
            raise TypeError("Influencer was not added since an invalid influencer_rules_or_weight was given.")


class RationallyPerceivedKnowledge(FastDynamicsVariable):
    def __init__(self, name, initial_value=0, initial_influencers=(), range_values=(-1, 1), verbal_terms=tuple(),
                 mf_type='default', update_rate=1, bound_variable=None, incremental_variable=False, incremental_var_slow=False):
        super().__init__(name, initial_value, initial_influencers, range_values, verbal_terms, mf_type)
        self.influencers_types = []


class PerceivedKnowledge(FastDynamicsVariable):
    def __init__(self, name, initial_value=0, initial_influencers=(), range_values=(-1, 1), verbal_terms=tuple(),
                 mf_type='default', update_rate=1, bound_variable=None, incremental_variable=False, incremental_var_slow=False):
        super().__init__(name, initial_value, initial_influencers, range_values, verbal_terms, mf_type)
        self.influencers_types = [RationallyPerceivedKnowledge, Bias]


class Belief(FastDynamicsVariable):
    def __init__(self, name, initial_value=0, initial_influencers=(), range_values=(-1, 1), verbal_terms=tuple(),
                 mf_type='default', update_rate=1, bound_variable=None, incremental_variable=False, incremental_var_slow=False):
        super().__init__(name, initial_value, initial_influencers, range_values, verbal_terms, mf_type, update_rate,
                         bound_variable, incremental_variable, incremental_var_slow)
        self.influencers_types = (RationallyPerceivedKnowledge, PerceivedKnowledge, slow_dyn.GeneralWorldKnowledge, Bias)


class Goal(FastDynamicsVariable):
    def __init__(self, name, initial_value=0, initial_influencers=(), range_values=(-1, 1), verbal_terms=tuple(),
                 mf_type='default', update_rate=1, bound_variable=None, incremental_variable=False, incremental_var_slow=False):
        super().__init__(name, initial_value, initial_influencers, range_values, verbal_terms, mf_type, update_rate,
                         bound_variable, incremental_variable, incremental_var_slow)
        self.influencers_types = (Belief, slow_dyn.GeneralPreferences, Emotion, slow_dyn.PersonalityTraits)


class EmotionTrigger1(FastDynamicsVariable):
    def __init__(self, name, initial_value=0, initial_influencers=(), range_values=(-1, 1), verbal_terms=tuple(),
                 mf_type='default', update_rate=1):
        super().__init__(name, initial_value, initial_influencers, range_values, verbal_terms, mf_type, update_rate)
        self.influencers_types = (Belief, )


class EmotionTrigger2(FastDynamicsVariable):
    def __init__(self, name, initial_value=0, initial_influencers=(), range_values=(-1, 1), verbal_terms=tuple(),
                 mf_type='default', update_rate=1):
        super().__init__(name, initial_value, initial_influencers, range_values, verbal_terms, mf_type, update_rate)
        self.influencers_types = (Belief, Goal)


class EmotionTrigger3(FastDynamicsVariable):
    def __init__(self, name, initial_value=0, initial_influencers=(), range_values=(-1, 1), verbal_terms=tuple(),
                 mf_type='default', update_rate=1):
        super().__init__(name, initial_value, initial_influencers, range_values, verbal_terms, mf_type, update_rate)
        self.influencers_types = (Belief, slow_dyn.GeneralPreferences)


class Emotion(FastDynamicsVariable):
    def __init__(self, name, initial_value=0, initial_influencers=(), range_values=(-1, 1), verbal_terms=tuple(),
                 mf_type='default', update_rate=1, bound_variable=None, incremental_variable=False, incremental_var_slow=False):
        super().__init__(name, initial_value, initial_influencers, range_values, verbal_terms, mf_type, update_rate,
                         bound_variable, incremental_variable, incremental_var_slow)
        self.influencers_types = ([Belief], [Belief, Goal], [Belief, slow_dyn.GeneralPreferences],
                                  [Belief, Goal, slow_dyn.GeneralPreferences], [slow_dyn.PersonalityTraits], [Emotion])

    def is_influencer(self, influencer_):
        """ Checks whether a variable or a combination of variables is a side-linkage

        Parameters
        ----------
        influencer_ : Union[lib.model_elements.variables.fst_dynamics_variables.Belief, Tuple[lib.model_elements.variables.fst_dynamics_variables.Belief, lib.model_elements.variables.slow_dynamics_variables.GeneralPreferences], Tuple[lib.model_elements.variables.fst_dynamics_variables.Belief, lib.model_elements.variables.slow_dynamics_variables.GeneralPreferences], Tuple[lib.model_elements.variables.fst_dynamics_variables.Belief, lib.model_elements.variables.slow_dynamics_variables.GeneralPreferences]]
            either one variable influencer, or a list that contains the influencer and the side_linkage
        Returns
        -------
        Union[None, bool]
        """
        for inf_type in self.influencers_types:
            if not isinstance(influencer_, (list, tuple)):
                influencer_ = [influencer_]
            if len(inf_type) == len(influencer_):
                # all elements of influencer_ (inf and side linkage) correspond to a valid combination of inf and SL
                if all(isinstance(influencer_[i], inf_type[i]) for i in range(len(influencer_))):
                    return True
        return False

    def add_one_influencer(self, new_influencer, influencer_rules_or_weight=None, influencer_side_linkage=None,
                           inf_boundary_values=(-1, 1)):
        if influencer_side_linkage is not None:
            if not self.is_influencer((new_influencer, influencer_side_linkage)):
                raise TypeError('Complex linkage has a wrong type of influencer or of the side linkage.')
        super().add_one_influencer(new_influencer, influencer_rules_or_weight, influencer_side_linkage, inf_boundary_values)

    @deprecation.deprecated()
    def add_influencer_variables(self, new_influencer):
        if type(new_influencer) is not list:   # in case there is only one element, it is made a list
            new_influencer = [new_influencer]
        elif len(new_influencer) == 2:  # in case the list is one element and a value
            if core_variables.is_pair_variable_value(new_influencer):
                new_influencer = [new_influencer]
        topop = []
        for i in range(len(new_influencer)):
            if not isinstance(new_influencer[i], list):
                if type(new_influencer[i]) is Belief:
                    if i < len(new_influencer) - 1:
                        if type(new_influencer[i+1]) in influencer.Influencer.connection_type:
                            new_influencer[i] = [new_influencer[i], new_influencer[i+1]]
                            topop.append(i+1)
                        else:
                            new_influencer[i] = [new_influencer[i]]
                    else:
                        new_influencer[i] = [new_influencer[i]]
        for i in range(len(topop)):
            new_influencer.pop(topop[i]-i)
        # At this point, new_influencer is a list of influencers
        for i in range(len(new_influencer)):   # we have 2 cases of element in this list
            if isinstance(new_influencer[i], list):
                if type(new_influencer[i][-1]) in influencer.Influencer.connection_type:    # if element is variable + value
                    influencer_weight = new_influencer[i].pop()
                else:
                    influencer_weight = 0
                if self.is_influencer(new_influencer[i]):
                    if len(new_influencer[i]) == 1:
                        self.influencers.append(influencer.Influencer(new_influencer[i][0], influencer_weight))
                    else:
                        self.influencers.append(influencer.Influencer(new_influencer[i][0], influencer_weight, True,
                                                                      new_influencer[i][1]))
                else:
                    raise TypeError("Type of influencer is not allowed", type([new_influencer[i][0]]))
            elif isinstance(new_influencer[i], Belief):
                self.influencers.append(influencer.Influencer(new_influencer[i][0], 0))
            else:
                raise TypeError("Influencer is not of a correct type. Is of type ", type(new_influencer[i]))


class Bias(FastDynamicsVariable):
    def __init__(self, name, initial_value=0, initial_influencers=(), range_values=(-1, 1), verbal_terms=tuple(),
                 mf_type='default', update_rate=1, bound_variable=None, incremental_variable=False, incremental_var_slow=False):
        super().__init__(name, initial_value, initial_influencers, range_values, verbal_terms, mf_type,
                         bound_variable=bound_variable)
        self.influencers_types = (Goal, Emotion, slow_dyn.PersonalityTraits)


class BeliefData(FastDynamicsVariable):
    def __init__(self, name, data=None, influencer_=None):
        super().__init__(name, initial_value=0, initial_influencers=())
        self.value = data
        self.influencers = influencer_
        self.influencers_types = (lib.tom_model.model_elements.variables.perception_variables.PerceivedKnowledgeSet,)

    def compute_variable_value_fcm(self):
        self.compute_new_value()

    def compute_variable_value_fis(self):
        self.compute_new_value()

    def compute_new_value(self):
        assert type(self.value) == type(self.influencers.raw_data)
        self.next_value = copy.deepcopy(self.influencers.raw_data)

    def update_value(self):
        self.value = copy.deepcopy(self.next_value)


class BoundMethod(Enum):
    NONE = 1
    TANH = 2
    CLIP = 3
