from lib.tom_model.model_elements.processes import action_selector, intention_selector


class DecisionMakingModule:
    def __init__(self, intention_selector_process: intention_selector.IntentionSelector,
                 action_selector_process: action_selector.ActionSelector):
        """ Declares decision-making module based on the two processes (intention selection and action selection)
        and their outputs, which are the main variables of the decision-making module

        Parameters
        ----------
        intention_selector_process : Intention Selector Process
        action_selector_process : Action Selector Process
        """
        self.intention_selector = intention_selector_process
        self.action_selector = action_selector_process

    def compute_new_value(self, compute_action=True):
        """ Computes the new values of the intention and action by executing the intention selector and action selector
        processes.

        Parameters
        ----------
        compute_action : if the action is to be computed
        """
        self.intention_selector.compute_new_value()
        if compute_action:
            self.action_selector.compute_new_value()

    def update_values_of_module(self, update_action=True):
        """ Updated the values of the intention and action

        Parameters
        ----------
        update_action :  if the action is to be updated
        """
        self.intention_selector.update_value()
        if update_action:
            self.action_selector.update_value()

    def compute_and_update_module_in_1_go(self):
        """ Computes and updates the entire module at once, ignoring the time propagation caused by the state space
        ++ Pros: It is more efficient
        -- Cons: It does not respect state space formal representation if we consider model_structure as whole system.
               CAN ONLY be used if modules are independent systems

        """
        self.intention_selector.compute_new_value()
        self.intention_selector.update_value()
        self.action_selector.compute_new_value()
        self.action_selector.update_value()
