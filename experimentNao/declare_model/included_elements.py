class IncludedElements:
    def __init__(self, belief_made_progress: bool, belief_nao_helping: bool, belief_reward: bool,
                 belief_reward_hidden: bool, goal_reward: bool, goal_get_help: bool, emotion_happy: bool,
                 action_skip: bool, action_change_diff: bool, gp_challenged: bool, switch_get_help_influencer: bool,
                 inf_nao_hinders_on_get_help: bool, inf_nao_hinders_on_frustrated: bool,
                 inf_difficulty_on_skip: bool, inf_difficulty_on_frustrated: bool,
                 inf_made_progress_on_bored: bool, inf_bored_on_skip: bool,
                 all_scheduled_weights: bool, scheduled_weights_for_diff: bool, scheduled_weights_for_reward: bool,
                 emotion_self_influences: bool, bias_bored_on_diff: bool,
                 nonlinear_perception: bool, simplified_perception: bool,
                 bound_variables, incremental_variables: bool, incremental_var_slow:bool,
                 constrained_bias_weight: bool = False, vars_update_rate: float = 1.0):
        """ variables and linkages to be included in the model

        Parameters
        ----------
        belief_made_progress : bool
        belief_nao_helping : bool
        belief_reward : bool
        belief_reward_hidden : bool
        goal_reward : bool
        goal_get_help : bool
        emotion_happy : bool
        action_skip : bool
        action_change_diff : bool
        gp_challenged : bool
        switch_get_help_influencer : bool
        inf_nao_hinders_on_get_help : bool
        inf_nao_hinders_on_frustrated : bool
        inf_difficulty_on_skip : bool
        inf_difficulty_on_frustrated : bool
        inf_made_progress_on_bored : bool
        inf_bored_on_skip : bool
        all_scheduled_weights : bool
        scheduled_weights_for_diff : bool
        scheduled_weights_for_reward : bool
        emotion_self_influences : bool
        bias_bored_on_diff : bool
        nonlinear_perception : bool
        simplified_perception : bool
        bound_variables : lib.tom_model.model_elements.variables.fst_dynamics_variables.BoundMethod
        incremental_variables : bool
        incremental_var_slow : bool
        constrained_bias_weight : bool
        vars_update_rate : float
        """
        # Included variables
        self.belief_made_progress = belief_made_progress
        self.belief_nao_helping = belief_nao_helping
        self.belief_reward = belief_reward
        self.belief_reward_hidden = belief_reward_hidden
        self.goal_reward = goal_reward
        self.goal_get_help = goal_get_help
        self.emotion_happy = emotion_happy
        self.action_skip = action_skip
        self.action_change_diff = action_change_diff
        self.gp_challenged = gp_challenged
        # Included linkages
        self.switch_get_help_influencer = switch_get_help_influencer
        self.influence_nao_hinders_on_get_help = inf_nao_hinders_on_get_help
        self.influence_nao_hinders_on_frustrated = inf_nao_hinders_on_frustrated
        self.influence_difficulty_on_skip = inf_difficulty_on_skip
        self.influence_difficulty_on_frustrated = inf_difficulty_on_frustrated
        self.influence_made_progress_on_bored = inf_made_progress_on_bored
        self.influence_bored_on_skip = inf_bored_on_skip
        self.all_scheduled_weights = all_scheduled_weights
        self.scheduled_weights_for_diff = scheduled_weights_for_diff
        self.scheduled_weights_for_reward = scheduled_weights_for_reward
        self.bias_bored_on_diff = bias_bored_on_diff
        # Model update
        self.emotion_self_influences = emotion_self_influences
        self.vars_update_rate = vars_update_rate
        self.bound_variables = bound_variables
        self.constrained_bias_weight = constrained_bias_weight
        self.nonlinear_perception = nonlinear_perception
        self.simplified_perception = simplified_perception
        self.incremental_variables = incremental_variables
        self.incremental_var_slow = incremental_var_slow
        if self.belief_reward_hidden:    # if variable is hidden, make sure the variable was toggled on
            assert self.belief_reward
