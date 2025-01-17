from lib.tom_model.model_structure import cognitive_module, perception_module, decision_making_module, tom_model
from lib.tom_model.usage_example import declare_variables, declare_cognitive_module, declare_decision_making, \
    declare_perception_module


def declare_model():
    # All vars
    beliefs, goals, emotions, biases, rpk, pk, gps, pts, intentions, actions, rld, pd, pk_set \
        = declare_variables.declare_all_variables()

    # Cognitive
    beliefs, goals, emotions, biases, pk, gps, pts \
        = declare_cognitive_module.declare_all_linkages(beliefs, goals, emotions, biases, rpk, pk, gps, pts)
    cognitive = cognitive_module.CognitiveModule(beliefs, goals, emotions, biases, pk, general_world_knowledge=(),
                                                 general_preferences=gps, personality_traits=pts)

    # Decision
    intention_selector = declare_decision_making.FoodIntentionSelector(beliefs, goals, intentions)
    action_selector = declare_decision_making.FoodActionSelector(intentions, actions)
    decision_making = decision_making_module.DecisionMakingModule(intention_selector, action_selector)

    # Perception
    perceptual_access_process = declare_perception_module.FoodPerceptualAccess(rld, pd)
    rational_reasoning_process = declare_perception_module.FoodRationalReasoning(pd, pk_set)
    perception = perception_module.PerceptionModule(perceptual_access_process, rational_reasoning_process)

    model = tom_model.TomModel(cognitive, decision_making, perception, time_steps4convergence=5)
    return model
