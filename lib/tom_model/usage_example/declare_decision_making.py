from lib.tom_model.model_elements.processes import action_selector, intention_selector
from lib.tom_model.model_elements.variables import fst_dynamics_variables, decision_making_variables


class ActionEating(decision_making_variables.Action):
    def __init__(self, name, food, verbal_terms=()):
        super().__init__(name, action=ActionEating.eat, verbal_terms=verbal_terms)
        self.active = False
        self.food = food

    def eat(self):
        pass    # declare here what happens if observed agent makes action


class IntentionEating(decision_making_variables.Intention):  # you can also inherit the already defined child class of
    def __init__(self, name, goal, belief=None, food=None, verbal_terms=()):  # Intention, 'IntentionThreshold', if you
        super().__init__(name, verbal_terms)                                  # plan to use IntentionSelectorThreshold
        self.active = False
        self.food = food
        self.add_influencer(goal, belief)

    def add_influencer(self, goal, belief=None):
        assert isinstance(goal, fst_dynamics_variables.Goal)
        self.goal = goal
        if belief is not None:
            assert isinstance(belief, fst_dynamics_variables.Belief)
            self.belief = belief


class FoodIntentionSelector(intention_selector.IntentionSelector):  # you can also inherit one of the already defined
    def __init__(self, all_beliefs, all_goals, all_intentions):     # child classes of IntentionSelector, where:
        all_beliefs = turn_dict_into_tuple(all_beliefs)             # (threshold and highest goal)
        all_goals = turn_dict_into_tuple(all_goals)
        all_intentions = turn_dict_into_tuple(all_intentions)
        super().__init__(inputs=(all_beliefs, all_goals), outputs=all_intentions,
                         function=FoodIntentionSelector.intention_selection,
                         input_type=(fst_dynamics_variables.Belief, fst_dynamics_variables.BeliefData,
                                     fst_dynamics_variables.Goal),
                         output_type=IntentionEating)

    def intention_selection(self):
        pass    # define here how the intentions are selected


class FoodActionSelector(action_selector.ActionSelector):
    def __init__(self, all_intentions, all_actions):
        all_intentions = turn_dict_into_tuple(all_intentions)
        all_actions = turn_dict_into_tuple(all_actions)
        super().__init__(inputs=all_intentions, outputs=all_actions,
                         function=FoodActionSelector.action_selection,
                         input_type=IntentionEating,
                         output_type=ActionEating)
        assert len(self.inputs) == len(self.outputs)
        self.current_action = None

    def action_selection(self):
        pass  # define here how the actions are selected


def turn_dict_into_tuple(my_list):
    return my_list if isinstance(my_list, (list, tuple)) else tuple(my_list.values())
