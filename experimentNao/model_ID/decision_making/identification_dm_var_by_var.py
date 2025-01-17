from experimentNao.model_ID.decision_making import set_values_of_variables_dm as set_values, identification_dm as id_dm
from lib import excel_files


class DMIdentification1by1(id_dm.DMIdentification):
    def identify_and_test(self):
        """ runs the identification and testing of the decision-making module

        """
        for intentions in self.get_intentions_grouped(get_keywords_of_groups_of_intentions()):
            print('\n*** Intentions: ', [intention.name for intention in intentions])
            time_steps = self.set_values_of_group(intentions)
            train_steps, test_steps, t_steps_aggregated = self.select_train_and_valid_data(time_steps)
            print_intention_values(intentions)
            # Identification
            self.identify_dm(train_steps, intentions)
            df_of_intention = self.output_identification_info(train_steps, intentions[0])
            # Testing
            test_costs = self.test_dm(test_steps, intentions)
            # Choose parameter for MBC
            most_accurate_threshold = self.choose_best_param_mbc(intentions)
            df_of_intention = self.output_testing_info(df_of_intention, test_costs, test_steps,
                                                       most_accurate_threshold, intentions)
        excel_files.save_df_to_excel_sheet(self.writer, self.df_best_parameters, 'List of Parameters')

    def cost_function(self, parameters, train_steps, intentions):
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
        self.parameters_manager.set_values_of_thresholds(intentions, parameters)
        cost = 0
        for step in train_steps:
            # 1. Set values of variables in time step
            for intention in intentions:
                intention.goal.value = intention.goal.values[step]
                if intention.belief is not None:
                    intention.belief.value = intention.belief.values[step]
            # 2. Run intentions
            self.dm_module.intention_selector.deactivate_all_intentions()
            for intention in intentions:
                self.dm_module.intention_selector.activate_1_intention_by_threshold_fast(intention)
            # 3. Compute cost
            for intention in intentions:
                cost += self.cost_of_predicting_intention(intention, step)
        return cost
    
    def test_dm(self, test_steps, intentions_group):
        """ test the performance of the identified decision-making module

        Parameters
        ----------
        test_steps : List[int]
        intentions_group : List[experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame]

        Returns
        -------
        List[int]
        """
        costs = []
        for set_of_params in self.optimal_parameters_values:
            costs.append(0)
            for i in range(len(self.parameters_list)):
                self.parameters_list[i].value = set_of_params[i]
            costs[-1] += self.cost_function(self.parameters_list, test_steps, intentions_group)
        return costs

    @staticmethod
    def choose_best_param_mbc(intentions_group):
        """ For each group of intentions (group of intention(s) linked to the same goal G), select parameters of its
        rational intention selection function that should be used in the model-based controller. If the action was taken
        by the participant at least once in the interactions, select the parameter identified during the identification
        process; Otherwise, generate the most suitable value for the threshold according to the data about the goal G
        collected in the interaction with the participant.

        Parameters
        ----------
        intentions_group : List[experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame]

        Returns
        -------
        List[numpy.float64]
        """
        most_accurate_threshold = []
        for intention in intentions_group:
            if not any(intention.intentions_sequence):  # participant did not take action even once
                if intention.larger_than_threshold:
                    largest_goal_value = max(intention.goal.values)     # the largest goal measured in the interaction
                    predicted_value = min((largest_goal_value+1)/2, 1)  # average between the largest goal and 1
                else:
                    smallest_goal_value = min(intention.goal.values)
                    predicted_value = max((smallest_goal_value + -1) / 2, -1)
                most_accurate_threshold.append(predicted_value)
            else:                                       # if participant took the action, just keep the chosen value
                most_accurate_threshold.append(None)    # saving "None" for now in the list of 'most_accurate_threshold'
        return most_accurate_threshold

    # **********************************************************************************************************************
    #                                            Organize Information
    # **********************************************************************************************************************
    def set_values_of_group(self, intentions_group):
        """ sets the list of values of the intentions in a group from the "files".

        Parameters
        ----------
        intentions_group : List[experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame]
            A group of intention(s) linked to the same goal

        Returns
        -------
        List[range]
        """
        for i in range(len(intentions_group)):
            time_steps = set_values.set_values_of_1_var_for_dm(self.dm_module, self.reader, self.n_puzzles,
                                                               self.get_equivalent_action(intentions_group[i]),
                                                               set_influencer_values=True if i == 0 else False)
        return time_steps
    
    def get_intentions_grouped(self, keywords_groups):
        """ Distributes the intentions into groups of intention(s) linked to the same goal or the same goal/belief pair

        Parameters
        ----------
        keywords_groups : List[List[str]]

        Returns
        -------
        List[List[experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame]]
        """
        grouped_intentions = []
        for keywords in keywords_groups:
            grouped_intentions.append(self.get_group_of_intentions(keywords))
        return grouped_intentions
    
    def get_group_of_intentions(self, keywords):
        """ returns the list of intentions that are related to a goal by searching for a keyword in the names of the
        intentions.

        Parameters
        ----------
        keywords : List[str]

        Returns
        -------
        List[experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame]
        """
        return [int_ for int_ in self.get_all_intentions if all(keyword in int_.name for keyword in keywords)]
    
    def get_equivalent_action(self, intention):
        """ returns the action that is linked to a specific intention

        Parameters
        ----------
        intention : experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame

        Returns
        -------
        experimentNao.declare_model.modules.declare_decision_making.ActionChessGame
        """
        return next((action for action in self.get_all_actions() if action.name == intention.name), None)


def get_keywords_of_groups_of_intentions():
    """ returns the list of groups of strings connected to each group of intentions. Each list corresponds to one group
    of intentions.

    Returns
    -------
    List[List[str]]
    """
    return [['skip'], ['help'], ['quit'], ['ask for', 'game']]


def print_intention_values(intentions):
    """ prints the sequence of realisations of each intention from the , as well as the sequence of realisations of the goals and beliefs associated with that intention.

    Parameters
    ----------
    intentions : List[experimentNao.declare_model.modules.declare_decision_making.IntentionChessGame]
    """
    for intention in intentions:
        print('\t *** Values of action variable: ', intention.intentions_sequence)
        print('\t *** Values of goal:  ', [round(ele, 2) for ele in intention.goal.values])
        if intention.belief is not None:
            print('\t *** Values of belief: ', [round(ele, 2) for ele in intention.belief.values])
