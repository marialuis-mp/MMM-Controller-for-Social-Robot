from lib.tom_model.fis_support_functions import fis_rules as rules
from lib.tom_model.model_elements.variables import cognitive_variables
from lib.tom_model.model_elements.linkage.scheduled_weight import ScheduledWeight
from lib.tom_model import config
from lib.util import *


@static_init
class Influencer:
    connection_type = []

    @classmethod
    def static_init(cls):
        if config.FRAMEWORK == "FCM":
            setattr(cls, "connection_type", [int, float, ScheduledWeight])
        if config.FRAMEWORK == "FIS":
            setattr(cls, "connection_type", [rules.RuleSet])

    def __init__(self, inf_var, inf_w, side_linkage=False, side_linkage_variable=None, boundary_values=(-1, 1)):
        if isinstance(inf_var, cognitive_variables.CognitiveVariable):
            self.influencer_variable = inf_var
        else:
            raise TypeError("Influencer variable must be an element")
        if type(inf_w) in Influencer.connection_type:
            self.influencer_linkage = inf_w
        else:
            raise TypeError("Influencer weight must be of type " + Influencer.connection_type)
        self.has_side_linkage = side_linkage
        if side_linkage and isinstance(side_linkage_variable, cognitive_variables.CognitiveVariable):
            self.side_linkage = side_linkage_variable
        if config.FRAMEWORK == 'FCM':
            self.boundary_values = boundary_values


    def add_more_rules(self, new_rule_set):
        if type(new_rule_set) in Influencer.connection_type:
            self.influencer_linkage = self.influencer_linkage + new_rule_set
