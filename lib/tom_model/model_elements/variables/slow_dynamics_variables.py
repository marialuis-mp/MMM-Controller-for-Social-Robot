from lib.tom_model.model_elements.variables import cognitive_variables
from abc import ABCMeta


class SlowDynamicsVariable(cognitive_variables.CognitiveVariable):
    __metaclass__ = ABCMeta

    def __init__(self, name, initial_value=0, range_values=(-1, 1), verbal_terms=tuple(), mf_type='default'):
        super().__init__(name, initial_value, range_values, verbal_terms, mf_type)
        self.frequency = 0.01


class GeneralWorldKnowledge(SlowDynamicsVariable):
    def is_influencer(self, influencer):
        influencers_types = []
        return type(influencer) in influencers_types


class GeneralPreferences(SlowDynamicsVariable):
    def is_influencer(self, influencer):
        return False


class PersonalityTraits(SlowDynamicsVariable):
    def is_influencer(self, influencer):
        influencers_types = []
        return type(influencer) in influencers_types
