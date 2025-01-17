import time

from experimentNao.model_ID.decision_making import set_values_of_variables_dm as set_values, identification_dm as id_dm


class DMIdentificationAll(id_dm.DMIdentification):
    def identify_and_test(self):
        """ runs the identification and testing of the decision-making module

        """
        time_steps = set_values.set_values_of_vars_for_dm(self.dm_module, self.reader, self.n_puzzles,
                                                          set_influencer_values=True)
        train_steps, test_steps, t_steps_aggregated = self.select_train_and_valid_data(time_steps)
        # Identification
        st = time.time()
        self.identify_dm(train_steps, self.get_all_intentions)
        print('*** Time for training:', st - time.time())
        df_all = self.output_identification_info(train_steps)
        # Testing
        test_costs = self.test_dm(test_steps, verbose=1)
        df_all = self.output_testing_info(df_all, test_costs, test_steps)

    def cost_function(self, parameters, train_steps, intentions=None):
        """ cost function for the identification process. This function computes a cost that reflects how incorrect
        the predictions (about the intentions) done by the model are with respect to the ground truth (train or test
        data), depending on the current parameters of the decision-making module.

        Parameters
        ----------
        parameters : List[lib.algorithms.gradient_descent.parameters2optimise.Parameter2Optimise]
        train_steps : List[int]
        intentions : List[experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame]

        Returns
        -------
        int
        """
        self.parameters_manager.set_values_of_thresholds(self.get_all_intentions, parameters)
        cost = 0
        for step in train_steps:
            # 1. Set values of variables in time step
            for input_ in self.dm_module.intention_selector.inputs:
                input_.value = input_.values[step]
            # 2. Run intentions
            self.dm_module.intention_selector.compute_new_value()
            # 3. Compute cost
            for intention in self.get_all_intentions:
                cost += self.cost_of_predicting_intention(intention, step)
        return cost

    def test_dm(self, test_steps, verbose):
        """ test the performance of the identified decision-making module

        Parameters
        ----------
        test_steps : List[int]
        verbose : int

        Returns
        -------
        List[int]
        """
        test_costs = []
        for set_of_params in self.optimal_parameters_values:
            test_costs.append(0)
            for i in range(len(self.parameters_list)):
                self.parameters_list[i].value = set_of_params[i]
            for intention in self.get_all_intentions:
                test_costs[-1] += self.cost_function(self.parameters_list, test_steps)
                if verbose > 1:
                    print(intention.name, ' - cost: ', test_costs[-1])
        return test_costs
