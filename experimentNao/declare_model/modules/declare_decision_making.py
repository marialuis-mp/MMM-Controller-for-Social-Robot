import lib.tom_model.model_elements.variables.decision_making_variables
from lib.tom_model.model_elements.processes import action_selector, intention_selector
from lib.tom_model.model_elements.variables import fst_dynamics_variables, outer_variables


class ActionChessGame(lib.tom_model.model_elements.variables.decision_making_variables.Action):
    def __init__(self, name, verbal_terms=()):
        """ actions that the participant can do in the interaction of playing chess games with Nao

        Parameters
        ----------
        name : str
        verbal_terms : List[str]
        """
        super().__init__(name, action=ActionChessGame.do_nothing, verbal_terms=verbal_terms)
        self.active = False
        self.actions_sequence = []

    def do_nothing(self):
        pass

    def activate(self):
        """ set action as active

        """
        self.active = True

    def deactivate(self):
        """ set action as inactive

        """
        self.active = False


class IntentionChessGame(lib.tom_model.model_elements.variables.decision_making_variables.IntentionThreshold):
    def __init__(self, name, threshold, goal, belief=None, belief_contribution=0, verbal_terms=(),
                 larger_than_threshold=True):
        """ intentions that the participant can have in the interaction of playing chess games with Nao

        Parameters
        ----------
        name : str
        threshold : float
        goal : lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal
        belief : Union[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
        belief_contribution : int
        verbal_terms : List[str]
        larger_than_threshold : bool
        """
        super().__init__(name, threshold, goal, belief, belief_contribution, verbal_terms, larger_than_threshold)


class HumanIntentionSelector(intention_selector.IntentionSelectorThreshold):
    def __init__(self, all_beliefs, all_goals, all_intentions):
        """ Rational intention selection for the interaction of playing chess games with Nao

        Parameters
        ----------
        all_beliefs : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]
        all_goals : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal]
        all_intentions : List[experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame]
        """
        all_beliefs = turn_dict_into_tuple(all_beliefs)
        all_goals = turn_dict_into_tuple(all_goals)
        all_intentions = turn_dict_into_tuple(all_intentions)
        super().__init__(inputs=(all_beliefs, all_goals), outputs=all_intentions,
                         function=intention_selector.IntentionSelectorThreshold.activate_intentions_by_threshold_fast,
                         input_type=(fst_dynamics_variables.Belief, fst_dynamics_variables.Goal),
                         output_type=IntentionChessGame)


class HumanActionSelector(action_selector.ActionSelector):
    def __init__(self, all_intentions, all_actions):
        """ Rational action selection for the interaction of playing chess games with Nao

        Parameters
        ----------
        all_intentions : List[experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame]
        all_actions : List[experimentNao.declare_model.modules.declare_decision_making.ActionChessGame]
        """
        all_intentions = turn_dict_into_tuple(all_intentions)
        all_actions = turn_dict_into_tuple(all_actions)
        super().__init__(inputs=all_intentions, outputs=all_actions,
                         function=HumanActionSelector.one,
                         input_type=IntentionChessGame,
                         output_type=ActionChessGame)
        assert len(self.inputs) == len(self.outputs)
        self.current_actions = None

    def one(self):
        """ chooses the first action whose intention is active

        """
        for action in self.outputs:
            action.deactivate()
        self.current_actions = list()
        for i in range(len(self.inputs)):
            if self.inputs[i].active:
                self.current_actions.append(self.outputs[i])
                self.outputs[i].activate()


def turn_dict_into_tuple(my_list):
    return my_list if isinstance(my_list, (list, tuple)) else tuple(my_list.values())
