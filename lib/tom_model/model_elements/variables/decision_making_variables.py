from lib.tom_model.model_elements.variables.outer_variables import OuterElement
from lib.tom_model.model_elements.variables import fst_dynamics_variables


class Action(OuterElement):
    def __init__(self, name: str, action, verbal_terms=()):
        """ Action variable, which is the output of the decision-making module.

        Parameters
        ----------
        name : str
            Name that identifies the action.
        action : function
            The function that is called when the action is chosen. This is relevant when we want to propagate the
            actions of the agent into the real world.
        verbal_terms: tuple
            List of verbal terms associated with the action. It is optional
        """
        super().__init__(name, verbal_terms)
        assert callable(action)
        self.action = action


class Intention(OuterElement):
    def __init__(self, name: str, object_of_var=None, verbal_terms=()):
        super().__init__(name, verbal_terms)
        self.object_of_variable = object_of_var  # if there are many B,G,E about many entities, the entity this var is about
        self.goal = None
        self.belief = None


class IntentionThreshold(Intention):
    def __init__(self, name, threshold, goal, belief=None, belief_contribution=0, verbal_terms=(),
                 larger_than_threshold=True):
        super().__init__(name, verbal_terms)
        self.threshold = threshold
        self.active = False
        self.intentions_sequence = []
        self.belief_contribution = 0
        self.larger_than_threshold = larger_than_threshold
        self.add_influencer(goal, belief, belief_contribution)

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def add_influencer(self, goal, belief=None, belief_contribution=0):
        assert isinstance(goal, fst_dynamics_variables.Goal)
        self.goal = goal
        if belief is not None:
            assert isinstance(belief, fst_dynamics_variables.Belief)
            self.belief = belief
            self.belief_contribution = belief_contribution
