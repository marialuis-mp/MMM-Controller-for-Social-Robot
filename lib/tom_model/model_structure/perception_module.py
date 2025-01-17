from lib.tom_model.model_elements.processes import rational_reasoning, perceptual_access


class PerceptionModule:
    def __init__(self,
                 perceptual_access_process: perceptual_access.PerceptualAccess,
                 rational_reasoning_process: rational_reasoning.RationalReasoning):
        """ Declares modules module based on the two processes (perceptual access and rational reasoning) and their
        outputs, which are the main variables of the modules module

        Parameters
        ----------
        perceptual_access_process : Perceptual Access Process
        rational_reasoning_process : Rational Reasoning Process
        """
        self.perceptual_access = perceptual_access_process
        self.perceived_data = perceptual_access_process.outputs
        self.rational_reasoning = rational_reasoning_process
        self.perceived_knowledge = rational_reasoning_process.outputs

    def compute_new_value(self):
        """ Computes the new values of the perceived data and perceive knowledge by executing the perceptual access and
        rational reasoning, respectively.

        """
        self.perceptual_access.compute_new_value()
        self.rational_reasoning.compute_new_value()

    def update_values_of_module(self):
        """ Updates the new values of the perceived data and perceive knowledge.

        """
        self.perceptual_access.update_value()
        self.rational_reasoning.update_value()      # computes both the knowledge and the data in perceived knowledge

    def get_overall_output(self, include_raw_data=False):
        """ Returns the external output of the modules module (the rationally perceived knowledge)

        Parameters
        ----------
        include_raw_data : whether the raw data is included (True) or only the propositional types of knowledge are included

        Returns
        -------

        """
        if include_raw_data:
            return self.perceived_knowledge
        else:
            return self.perceived_knowledge.knowledge

    def compute_and_update_module_in_1_go(self):
        """ Computes and updates the entire module at once, ignoring the time propagation caused by the state space
        ++ Pros: It is more efficient
        -- Cons: It does not respect state space formal representation if we consider model_structure as whole system.
               CAN ONLY be used if modules are independent systems

        """
        self.perceptual_access.compute_new_value()
        self.perceptual_access.update_value()
        self.rational_reasoning.compute_new_value()
        self.rational_reasoning.update_value()

    def get_module_outputs(self):
        """ Returns the overall outputs of the module

        Returns
        -------

        """
        return self.rational_reasoning.outputs
