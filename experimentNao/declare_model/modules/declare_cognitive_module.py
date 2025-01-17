from lib.tom_model.model_declaration_auxiliary import linkages_declaration_aux as aux
from lib.tom_model.model_elements.linkage.scheduled_weight import ScheduledWeight
from lib.tom_model.model_structure import cognitive_module
from lib.tom_model.model_elements.variables import fst_dynamics_variables


class CognitiveModuleChess(cognitive_module.CognitiveModule):
    def __init__(self, beliefs, goals, emotions, biases, pk, gps, pts):
        """ Cognitive Module of the tom model for the interaction of playing chess games with Nao

        Parameters
        ----------
        beliefs : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]
        goals : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal]
        emotions : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion]
        biases : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias]
        pk : Union[Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge], None, None, None, None, None, None, None, Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge], Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge], Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge], Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge], Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge], Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge]]
        gps : Dict[str, lib.tom_model.model_elements.variables.slow_dynamics_variables.GeneralPreferences]
        pts : Dict[str, lib.tom_model.model_elements.variables.slow_dynamics_variables.PersonalityTraits]
        """
        super().__init__(beliefs, goals, emotions, biases, perceived_knowledge=pk,
                         general_world_knowledge=(), general_preferences=gps, personality_traits=pts)
        self.state_vars = None
        self.aux_vars_biases, self.aux_vars_pks, self.aux_vars = None, None, None
        self.set_state_vars()
        self.set_auxiliary_vars()

    def compute_and_update_module(self, compute_biases=True):
        """ calculates and updates the values of the cognitive variables

        Parameters
        ----------
        compute_biases : bool
        """
        self.compute_and_update_state_variables()  # compute each var and then, update each var
        if compute_biases:
            self.compute_and_update_biases()  # again, biases are updated without dynamics

    def compute_and_update_state_variables(self):
        """ calculates and updates the values of the cognitive state variables

        """
        for var in self.state_vars:
            var.compute_variable_value_fcm()
        for var in self.state_vars:
            var.update_value()

    def compute_and_update_biases(self):
        """ calculates and updates the values of the biases variables

        """
        for bias in self.aux_vars_biases:  # all biases are computed and updated without dynamic
            bias.compute_variable_value_fcm()
            bias.update_value()

    def set_state_vars(self):
        """ sets the state variables (beliefs, goals, and emotions)

        """
        self.state_vars = self.get_beliefs() + self.get_goals() + self.get_emotions()

    def set_auxiliary_vars(self):
        """ sets the list of auxiliary variables

        """
        biases, pks = [], []
        for fst_dyn_var in self.state_vars:  # include parameters of influencers of respective bias
            if isinstance(fst_dyn_var, fst_dynamics_variables.Belief):
                for inf in fst_dyn_var.influencers:
                    if isinstance(inf.influencer_variable, fst_dynamics_variables.Bias):
                        biases.append(inf.influencer_variable)
                    if isinstance(inf.influencer_variable, fst_dynamics_variables.PerceivedKnowledge):
                        pks.append(inf.influencer_variable)
                        for inf2 in inf.influencer_variable.influencers:
                            if isinstance(inf2.influencer_variable, fst_dynamics_variables.Bias):
                                biases.append(inf2.influencer_variable)
        self.aux_vars_biases = tuple(biases)
        self.aux_vars_pks = tuple(pks)
        self.aux_vars = self.aux_vars_biases + self.aux_vars_pks

    def get_vars_2_id_and_hidden_vars(self, included_vars):
        """ returns the separate lists of the state variables whose parameters should be identified and of the state
        variables whose parameters are assumed to be known (hidden variables)

        Parameters
        ----------
        included_vars : experimentNao.declare_model.included_elements.IncludedElements

        Returns
        -------
        Tuple[List[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], List[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]]
        """
        return return_vars_2_id_and_hidden_vars(self.state_vars, included_vars)

    def get_vars_w_link_to_id(self, vars_2_id, simple_dynamics: bool):
        """ returns the list of the variables that have linkages with parameters to identify

        Parameters
        ----------
        vars_2_id : List[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]
        simple_dynamics : bool

        Returns
        -------
        Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion]
        """
        if not simple_dynamics:
            return tuple(tuple(vars_2_id) + self.aux_vars_biases)
        else:
            vars_w_linkages_to_id = []
            for var in vars_2_id:
                if not isinstance(var, fst_dynamics_variables.Belief):
                    vars_w_linkages_to_id.append(var)
                else:
                    for inf in var.influencers:
                        vars_w_linkages_to_id.append(inf.influencer_variable)
                        for inf2 in inf.influencer_variable.influencers:
                            if isinstance(inf2.influencer_variable, fst_dynamics_variables.Bias):
                                vars_w_linkages_to_id.append(inf2.influencer_variable)
            return tuple(vars_w_linkages_to_id)


def declare_all_linkages(beliefs, goals, emotions, biases, rpk, pk, gps, pts, included_vars, simplified_dynamics):
    """ declares the connections (linkages) that are part of the cognitive module

    Returns
    -------

    """
    bv_default = (-1, 1)
    bvs = BoundaryValues(beliefs_influenced=(0, 1),
                         goals_influenced=(-0.5, 0.5) if included_vars.incremental_variables else bv_default,
                         emotions_influenced=(-0.5, 0.5) if included_vars.incremental_variables else bv_default,
                         bias_influenced=(-0.5, 0.5) if included_vars.constrained_bias_weight else bv_default)
    if simplified_dynamics:
        beliefs, pk = declare_beliefs_influencers_simplified_dynamics(beliefs, pk, rpk, biases, included_vars, bvs)
    else:
        beliefs = declare_beliefs_influencers(beliefs, rpk, biases, included_vars, bvs)
    goals = declare_goals_influencers(included_vars, beliefs, goals, emotions, gps, bvs)
    emotions = declare_emotions_influencers(included_vars, beliefs, goals, emotions, pts, gps, bvs)
    biases = declare_biases_influencers(included_vars, biases, emotions, bvs)
    return beliefs, goals, emotions, biases, rpk, pk, gps, pts


def declare_beliefs_influencers(beliefs, rpk, biases, included_vars, boundary_values):
    """ declares the influencers of each one of the beliefs, assuming complex dynamics

    Parameters
    ----------
    beliefs : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]
    rpk : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.RationallyPerceivedKnowledge]
    biases : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias]
    included_vars : experimentNao.declare_model.included_elements.IncludedElements
    boundary_values : experimentNao.declare_model.modules.declare_cognitive_module.BoundaryValues

    Returns
    -------
    Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]
    """
    bv = boundary_values.bv_beliefs_influenced
    aux.add_several_influencers_simple(beliefs['game difficulty'], (rpk['game difficulty'], biases['game difficulty']), bv)
    if included_vars.belief_nao_helping:
        aux.add_several_influencers_simple(beliefs['nao helping'], (rpk['nao helping'], biases['nao helping']), bv)
    if included_vars.belief_reward:
        aux.add_several_influencers_simple(beliefs['nao offering rewards'], (rpk['nao offering rewards'],), bv)
        if not included_vars.belief_reward_hidden:
            aux.add_several_influencers_simple(beliefs['nao offering rewards'], (biases['nao offering rewards'],), bv)
    if included_vars.belief_made_progress:
        aux.add_several_influencers_simple(beliefs['made progress'], (rpk['made progress'], biases['made progress']), bv)
    return beliefs


def declare_beliefs_influencers_simplified_dynamics(beliefs, pk, rpk, biases, included_vars, boundary_values):
    """ declares the influencers of each one of the beliefs, assuming simplified dynamics

    Parameters
    ----------
    beliefs : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]
    pk : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge]
    rpk : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.RationallyPerceivedKnowledge]
    biases : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias]
    included_vars : experimentNao.declare_model.included_elements.IncludedElements
    boundary_values : experimentNao.declare_model.modules.declare_cognitive_module.BoundaryValues

    Returns
    -------
    Tuple[Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge]]
    """
    bv = boundary_values.bv_beliefs_influenced
    declare_pk_and_belief_influencers('game difficulty', beliefs, pk, rpk, biases, bv)
    if included_vars.belief_nao_helping:
        declare_pk_and_belief_influencers('nao helping', beliefs, pk, rpk, biases, bv)
    if included_vars.belief_reward:
        belief_name = 'nao offering rewards'
        aux.add_several_influencers_simple(beliefs[belief_name], (pk[belief_name], ), bv)
        aux.add_several_influencers_simple(pk[belief_name], (rpk[belief_name], ), bv)
        if not included_vars.belief_reward_hidden:
            aux.add_several_influencers_simple(pk[belief_name], (biases[belief_name], ), bv)
    if included_vars.belief_made_progress:
        declare_pk_and_belief_influencers('made progress', beliefs, pk, rpk, biases, bv)
    return beliefs, pk


def declare_pk_and_belief_influencers(belief_name, beliefs, pk, rpk, biases, bv):
    """ declares the influencers of each belief/perceived knowledge. Since each belief is associated to 1 pk, its easier
    to declare their influencers together.

    Parameters
    ----------
    belief_name : str
    beliefs : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]
    pk : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.PerceivedKnowledge]
    rpk : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.RationallyPerceivedKnowledge]
    biases : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias]
    bv : Tuple[int, int]
    """
    aux.add_several_influencers_simple(pk[belief_name], (rpk[belief_name], biases[belief_name]), bv)
    aux.add_several_influencers_simple(beliefs[belief_name], (pk[belief_name],), bv)


def add_several_influencers_sw_loc(included_vars, variable, influencers, boundary_values=None):
    """ local function that adds several influencers of a variable with scheduled weights, under the conditions of
    "included_vars". This local function adds the influencers, but only adds them with scheduled weights if the
    "included_vars" states "included_vars.all_scheduled_weights". Otherwise, only the variables in "sw_inf_names" are
    added with scheduled weights, and the other with simple weights. This function is implemented in this way following
    the tailored design of this experiment and its model.

    Parameters
    ----------
    included_vars : experimentNao.declare_model.included_elements.IncludedElements
    variable : Union[lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion]
    influencers : Union[Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion]]
    boundary_values : Tuple[float, float]
    """
    if included_vars.all_scheduled_weights:
        aux.add_several_influencers_w_sw(variable, influencers, boundary_values)
    else:
        # sw_inf_names: the influencers that always have scheduled weights
        sw_inf_names = ['game difficulty' if included_vars.scheduled_weights_for_diff else '',
                        'nao offering rewards' if included_vars.scheduled_weights_for_reward else '']
        sw_inf, other_infs = [], []
        for inf in influencers:
            if isinstance(inf, fst_dynamics_variables.Belief) and inf.name in sw_inf_names:
                sw_inf.append(inf)
            else:
                other_infs.append(inf)
        aux.add_several_influencers_simple(variable, other_infs, boundary_values)
        aux.add_several_influencers_w_sw(variable, sw_inf, boundary_values)


def declare_goals_influencers(included_vars, beliefs, goals, emotions, general_preferences, boundary_values):
    """  declares the influencers of each one of the goals

    Parameters
    ----------
    included_vars : experimentNao.declare_model.included_elements.IncludedElements
    beliefs : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]
    goals : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal]
    emotions : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion]
    general_preferences : Dict[str, lib.tom_model.model_elements.variables.slow_dynamics_variables.GeneralPreferences]
    boundary_values : experimentNao.declare_model.modules.declare_cognitive_module.BoundaryValues

    Returns
    -------
    Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal]
    """
    bv = boundary_values.bv_goals_influenced
    # Quit game
    add_several_influencers_sw_loc(included_vars, goals['quit game'], (beliefs['game difficulty'],
                                                                       emotions['confident/frustrated'],
                                                                       emotions['interested/bored']), bv)
    if included_vars.belief_made_progress:
        add_several_influencers_sw_loc(included_vars, goals['quit game'], (beliefs['made progress'],), bv)
    goals['quit game'].add_one_influencer(general_preferences['chess preference'], inf_boundary_values=bv)     # no SW
    # Get help
    if included_vars.goal_get_help:
        if not included_vars.switch_get_help_influencer:
            add_several_influencers_sw_loc(included_vars, goals['get help'], (beliefs['game difficulty'],
                                                                              emotions['confident/frustrated']), bv)
        elif included_vars.belief_made_progress:
            add_several_influencers_sw_loc(included_vars, goals['get help'], (beliefs['made progress'],
                                                                              emotions['confident/frustrated']), bv)
        else:
            add_several_influencers_sw_loc(included_vars, goals['get help'], (emotions['confident/frustrated'],), bv)
        if included_vars.influence_nao_hinders_on_get_help and included_vars.belief_nao_helping:
            add_several_influencers_sw_loc(included_vars, goals['get help'], (beliefs['nao helping'],), bv)
    # Change game difficulty
    if included_vars.action_change_diff:
        add_several_influencers_sw_loc(included_vars, goals['change game difficulty'], (beliefs['game difficulty'],
                                                                                        emotions['confident/frustrated'],
                                                                                        emotions['interested/bored']), bv)
    if included_vars.goal_reward and included_vars.emotion_happy:
        add_several_influencers_sw_loc(included_vars, goals['get reward'], (emotions['interested/bored'],
                                                                            emotions['happy/unhappy']), bv)
    if included_vars.action_skip:
        add_several_influencers_sw_loc(included_vars, goals['skip puzzle'], (emotions['confident/frustrated'],), bv)
        if included_vars.influence_bored_on_skip:
            add_several_influencers_sw_loc(included_vars, goals['skip puzzle'], (emotions['interested/bored'],), bv)
        if included_vars.influence_difficulty_on_skip:
            add_several_influencers_sw_loc(included_vars, goals['skip puzzle'], (beliefs['game difficulty'],), bv)
        if included_vars.belief_made_progress:
            add_several_influencers_sw_loc(included_vars, goals['skip puzzle'], (beliefs['made progress'],), bv)
    return goals


def declare_emotions_influencers(included_vars, beliefs, goals, emotions, personality_traits, general_preferences,
                                 boundary_values):
    """  declares the influencers of each one of the emotions

    Parameters
    ----------
    included_vars : experimentNao.declare_model.included_elements.IncludedElements
    beliefs : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]
    goals : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal]
    emotions : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion]
    personality_traits : Dict[str, lib.tom_model.model_elements.variables.slow_dynamics_variables.PersonalityTraits]
    general_preferences : Dict[str, lib.tom_model.model_elements.variables.slow_dynamics_variables.GeneralPreferences]
    boundary_values : experimentNao.declare_model.modules.declare_cognitive_module.BoundaryValues

    Returns
    -------
    Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion]
    """
    bv = boundary_values.bv_emotions_influenced
    # Confident / Frustrated
    emotions['confident/frustrated'].add_one_influencer(personality_traits['self confident'], inf_boundary_values=bv)  # no SW
    if included_vars.belief_made_progress:
        add_several_influencers_sw_loc(included_vars, emotions['confident/frustrated'], (beliefs['made progress'],), bv)
    if included_vars.influence_difficulty_on_frustrated:
        add_several_influencers_sw_loc(included_vars, emotions['confident/frustrated'], (beliefs['game difficulty'],), bv)
    if included_vars.influence_nao_hinders_on_frustrated and included_vars.belief_nao_helping:
        add_several_influencers_sw_loc(included_vars, emotions['confident/frustrated'], (beliefs['nao helping'],), bv)
    if included_vars.belief_reward:
        add_several_influencers_sw_loc(included_vars, emotions['confident/frustrated'], (beliefs['nao offering rewards'],), bv)
        # Interested / Bored
        add_several_influencers_sw_loc(included_vars, emotions['interested/bored'], (beliefs['nao offering rewards'],), bv)
    if included_vars.belief_made_progress and included_vars.influence_made_progress_on_bored:
        add_several_influencers_sw_loc(included_vars, emotions['interested/bored'], (beliefs['made progress'],), bv)
    emotions['interested/bored'].add_one_influencer(personality_traits['focused'], inf_boundary_values=bv)  # no SW
    if included_vars.gp_challenged:
        emotions['interested/bored'].add_one_influencer(beliefs['game difficulty'],
                                                        influencer_rules_or_weight=ScheduledWeight(),
                                                        influencer_side_linkage=general_preferences['challenged preference'],
                                                        inf_boundary_values=bv)
    else:
        emotions['interested/bored'].add_one_influencer(beliefs['game difficulty'],
                                                        influencer_rules_or_weight=ScheduledWeight(),
                                                        inf_boundary_values=bv)
    # Unhappy / Happy
    if included_vars.emotion_happy:
        if included_vars.belief_made_progress:
            add_several_influencers_sw_loc(included_vars, emotions['happy/unhappy'], (beliefs['made progress'],))
        if included_vars.goal_reward and included_vars.belief_reward:
            emotions['happy/unhappy'].add_one_influencer(beliefs['nao offering rewards'],
                                                         influencer_rules_or_weight=ScheduledWeight(),
                                                         influencer_side_linkage=goals['get reward'],
                                                         inf_boundary_values=bv)
    # Self influence
    if included_vars.emotion_self_influences:
        for key in emotions:
            add_several_influencers_sw_loc(included_vars, emotions[key], (emotions[key],), bv)
    return emotions


def declare_biases_influencers(included_vars, biases, emotions, boundary_values):
    """  declares the influencers of each one of the biases

    Parameters
    ----------
    included_vars : experimentNao.declare_model.included_elements.IncludedElements
    biases : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias]
    emotions : Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion]
    boundary_values : experimentNao.declare_model.modules.declare_cognitive_module.BoundaryValues

    Returns
    -------
    Dict[str, lib.tom_model.model_elements.variables.fst_dynamics_variables.Bias]
    """
    bv = boundary_values.bv_bias_influenced
    add_several_influencers_sw_loc(included_vars, biases['game difficulty'], (emotions['confident/frustrated'],), bv)
    if included_vars.bias_bored_on_diff:
        add_several_influencers_sw_loc(included_vars, biases['game difficulty'], (emotions['interested/bored'],), bv)
    if included_vars.belief_made_progress:
        add_several_influencers_sw_loc(included_vars, biases['made progress'], (emotions['confident/frustrated'],), bv)
    if included_vars.belief_nao_helping:
        add_several_influencers_sw_loc(included_vars, biases['nao helping'], (emotions['confident/frustrated'],), bv)
    if included_vars.emotion_happy and included_vars.belief_reward and (not included_vars.belief_reward_hidden):
        add_several_influencers_sw_loc(included_vars, biases['nao offering rewards'], (emotions['happy/unhappy'],), bv)
    return biases


class BoundaryValues:
    def __init__(self, beliefs_influenced, goals_influenced, emotions_influenced, bias_influenced):
        """ defines the minimum and maximum values that each type of variables can have

        Parameters
        ----------
        beliefs_influenced : Tuple[int, int]
        goals_influenced : Tuple[float, float]
        emotions_influenced : Tuple[float, float]
        bias_influenced : Tuple[int, int]
        """
        self.bv_beliefs_influenced = beliefs_influenced
        self.bv_goals_influenced = goals_influenced
        self.bv_emotions_influenced = emotions_influenced
        self.bv_bias_influenced = bias_influenced


def return_vars_2_id_and_hidden_vars(state_vars, included_vars):
    """ returns the separate lists of the variables whose parameters should be identified and of the variables
        whose parameters are assumed to be known (hidden variables)

    Parameters
    ----------
    state_vars : Union[Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion], Tuple[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Goal, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion, lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion]]
    included_vars : experimentNao.declare_model.included_elements.IncludedElements

    Returns
    -------
    Tuple[List[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief], List[lib.tom_model.model_elements.variables.fst_dynamics_variables.Belief]]
    """
    vars_2_id, hidden_vars = [], []
    for var in state_vars:
        if included_vars.belief_reward_hidden and isinstance(var, fst_dynamics_variables.Belief) and 'reward' in var.name:
            hidden_vars.append(var)
        else:
            vars_2_id.append(var)
    return vars_2_id, hidden_vars
