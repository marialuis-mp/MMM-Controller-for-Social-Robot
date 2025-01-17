import copy

from experimentNao.declare_model import load_model
from experimentNao.model_ID.configs import model_configs
from lib import excel_files

from experimentNao.behaviour_controllers.mbc import aux_functions, controller_writer as wce, \
    model_propagator as mp, model_propagator_simple as mps, questions_manager as qm
from experimentNao.behaviour_controllers.mbc.aux_functions import print_values_of_computed_variables, \
    get_all_fast_dyn_vars, get_rpks_of_model
from experimentNao.behaviour_controllers.robot_action import RobotAction
from experimentNao.behaviour_controllers.controller import Controller
from experimentNao.declare_model import declare_entire_model as dem
from experimentNao.model_ID.cognitive import set_values_of_variables_cog


class ModelBasedController(Controller):
    def __init__(self, id_config, verbose=2, extra_predictive_step=True, for_interaction=True):
        """ Model-based controller used to control the behaviour of NAO in the third session, based on the model
        identified for the participant

        Parameters
        ----------
        id_config : experimentNao.model_ID.configs.overall_config.IDConfig
        verbose : int
        extra_predictive_step : bool
        for_interaction : bool
        """
        super().__init__()
        # decision variables
        self.next_puzzle_difficulty = None
        self.give_reward_selected = None
        self.actions = []
        self.set_all_actions()
        self.same_puzzle = True
        # Constraints
        self.hard_constraints = ['quit game', 'skip puzzle']
        if id_config.model_config == model_configs.ModelConfigs.SIMPLEST or \
                id_config.model_config == model_configs.ModelConfigs.SIMPLEST_W_BIAS or \
                id_config.model_config == model_configs.ModelConfigs.SIMPLEST_NO_SW_BIAS or \
                id_config.model_config == model_configs.ModelConfigs.SIMPLEST_W_BIAS_SLOW or \
                id_config.model_config == model_configs.ModelConfigs.SIMPLEST_NO_SW_BIAS_SLOW:
            self.soft_constraints = []
        else:
            self.soft_constraints = ['ask for easier game', 'ask for more difficult game']
        # Participant and models
        self.id_config = id_config
        self.file_cog, self.file_dm, self.file_metrics, self.included_variables \
            = load_model.get_files_with_parameters_and_metrics(self.id_config)
        rld_max_values = dem.get_normalization_values_of_rld(self.file_metrics, from_id=True)
        self.tom_model = dem.declare_model(self.included_variables, rld_max_values, id_config)
        self.tom_model_predictive = dem.declare_model(self.included_variables, rld_max_values, id_config)
        self.rld = self.tom_model.perception_module.perceptual_access.inputs
        if self.id_config.simple_dynamics:
            self.model_propagator = mps.ModelPropagationSimple(self.tom_model, self.tom_model_predictive, self.rld,
                                                               verbose, self.file_metrics, extra_predictive_step)
        else:
            self.model_propagator = mp.ModelPropagation(self.tom_model, self.tom_model_predictive, self.rld, verbose,
                                                        self.file_metrics, extra_predictive_step)
        self.ided_vars, self.hidden_vars = None, None
        self.load_model_parameters()
        self.n_horizon = id_config.n_horizon if id_config.simple_dynamics else 2
        self.extra_predictive_step = extra_predictive_step
        # Data output
        self.verbose = verbose
        self.for_interaction = for_interaction
        self.questions_manager = qm.QuestionsManagerMBC(puzzle_periodic_questions=True, time_periodic_questions=True)
        self.controller_writer = wce.WriteControllerToExcel(self.tom_model, self.actions, self.id_config)

    def initialize_controller(self, puzzle_difficulty, nao_helping, nao_offering_reward):
        """ initializes the variables of the controller

        Parameters
        ----------
        puzzle_difficulty : int
        nao_helping : bool
        nao_offering_reward : bool
        """
        # nao offering reward is used interchangeably for nao_offering_reward and reward_given
        self.next_puzzle_difficulty = puzzle_difficulty
        self.rld.data.fill_data(number_of_hints=0, number_of_wrong_attempts=[0], puzzle_difficulty=puzzle_difficulty,
                                prop_moves_revealed=0, time_2_solve=0, nao_helping=nao_helping,
                                nao_offering_reward=nao_offering_reward, reward_given=nao_offering_reward, skipped=False)

    def reset_beginning_of_puzzle(self, n_moves):
        """ resets the controller at the beginning of a puzzle

        Parameters
        ----------
        n_moves : int

        Returns
        -------
        bool
        """
        self.questions_manager.reset_beginning_of_puzzle()  # for questions to be asked
        return super().reset_beginning_of_puzzle(n_moves)

    def update_model_middle_of_question(self, current_rld, participant_answers, puzzle_counter, write=True):
        """ updates the values of the state variables of the model, either by asking the values to the participant
        or by using the model to estimate them. This is done depending on the output from self.questions_manager

        Parameters
        ----------
        current_rld : experimentNao.declare_model.chess_interaction_data.ChessInteractionData
        participant_answers : List[pandas.core.frame.DataFrame]
        puzzle_counter : int
        write : bool
        """
        if self.questions_manager.update_w_values_from_question:
            self.print_control_information('Update model from question')
            self.questions_manager.update_after_question_was_asked()
            self.update_model_from_question(participant_answers)
            updated_w_values_from_question = True
        else:   # if no question was asked, update model with dynamics
            self.print_control_information('Update model without question')
            current_rld = copy.deepcopy(current_rld)
            if self.id_config.normalise_rld_mid_steps:
                current_rld.normalise_mid_step()
            self.model_propagator.update_model_w_n_horizon(u_minus_1=current_rld, same_puzzle=self.same_puzzle)
            self.same_puzzle = True
            updated_w_values_from_question = False
        self.print_values_of_computed_variables(verbose=1)
        if write:
            self.controller_writer.write_mid_puzzle(puzzle_counter, self.get_puzzle_difficulty_status(),
                                                    updated_w_values_from_question)

    def update_end_of_puzzle_and_get_action(self, current_rld, puzzle_counter, write=True):
        """ updates the controller at the end of a puzzle (including the model) and gets the action chosen by the
        controller.

        Parameters
        ----------
        current_rld : experimentNao.declare_model.chess_interaction_data.ChessInteractionData
        puzzle_counter : int
        write : bool

        Returns
        -------
        experimentNao.behaviour_controllers.robot_action.RobotAction
        """
        current_rld = copy.deepcopy(current_rld)
        self.model_propagator.update_model_for_action_selection(current_rld)          # 0. Update model until x_{k-1}
        action = self.get_next_action(puzzle_counter, current_rld)
        self.set_next_action(action)
        self.print_control_information('Selected action:\t' + action.get_action_info())
        self.model_propagator.end_update_model_after_action_selection(action, current_rld)  # update model estimation
        self.same_puzzle = False
        self.print_values_of_computed_variables(verbose=1)
        if write:
            self.controller_writer.write_end_of_puzzle(self.actions, action, puzzle_counter)
        return action

    def get_next_action(self, puzzle_counter, current_rld):
        """ gets the next action chosen by the controller

        Parameters
        ----------
        puzzle_counter : int
        current_rld : experimentNao.declare_model.chess_interaction_data.ChessInteractionData

        Returns
        -------
        experimentNao.behaviour_controllers.robot_action.RobotAction
        """
        for action in self.actions:                                         # 1. Get cost and constraints of each action
            self.get_action_cost_and_constraints(action, current_rld)
        sorted_actions = sorted(self.actions, key=lambda act: act.cost)     # 2. sort actions by cost
        self.print_actions(sorted_actions)
        for action in sorted_actions:                                 # 3. The 1st action that satisfies all constraints
            if action.respects_all_constraints:
                return action                                               # 3a. Is selected
        self.print_control_information('Relaxed soft constraints')          # 3b. If none satisfies soft constraints
        for action in sorted_actions:                                 # 4. Do the same
            if action.respects_hard_constraints:
                return action
        self.print_control_information('Relaxed all constraints')           # 5. if none satisfies hard constraints,
        return sorted_actions[0]                                            # 6. Return action with min cost

    def get_action_cost_and_constraints(self, action, current_rld):
        """ gets the cost of choosing this "action" in the current moment with the current real life data 'current_rld'

        Parameters
        ----------
        action : experimentNao.behaviour_controllers.robot_action.RobotAction
        current_rld : experimentNao.declare_model.chess_interaction_data.ChessInteractionData
        """
        self.reset_predictive_model()                                   # 1. Reset the predictive model to current model
        self.model_propagator.run_predictive_model_w_action(action, current_rld)    # 2. Run model with the action
        action.set_cost(self.cost_function())                                       # 3. Save cost of action
        action.set_respected_constraints(*self.check_constraints())

    def reset_predictive_model(self):
        """ resets the values of the predictive model from the values saved in the current model. The predictive model
        is a virtual copy of the model that is propagated into the future with a certain action in order to check what
        are the consequences of taking that action. Since it is used to evaluate the future consequences of different
        actions, it needs to be reset before propagating it again.

        """
        vars_tom_model = get_all_fast_dyn_vars(self.tom_model)          # 1. Reset the predictive model to current model
        vars_predictive_model = get_all_fast_dyn_vars(self.tom_model_predictive)
        for i in range(len(vars_tom_model)):
            vars_predictive_model[i].value = vars_tom_model[i].value
            vars_predictive_model[i].values = copy.deepcopy(vars_tom_model[i].values)

    def cost_function(self):
        """ returns the cost of taking a specific action, in terms of the future mental states of the participant. The
        cost increases with the increase of the frustration, boredom, the desire to quit, the desire to skip a puzzle.
        It also increases if the participant perceived the puzzle as too difficult or to easy.
        Attention: To evaluate the cost of taking an action, this function must be called after propagating the
        predictive model.

        Returns
        -------
        numpy.float64
        """
        default_w = 1     # default weight
        cognitive_module = self.tom_model_predictive.cognitive_module
        if self.id_config.simple_dynamics:
            weights_dict = {cognitive_module.get_a_specific_emotion('confident/frustrated').name: [2*default_w, 0],
                            cognitive_module.get_a_specific_emotion('interested/bored').name: [2*default_w, 0],
                            cognitive_module.get_a_specific_goal('quit game').name: [2*default_w, 0],
                            cognitive_module.get_a_specific_goal('skip puzzle').name: [2*default_w, 0],
                            cognitive_module.get_a_specific_belief('game difficulty').name: [2*default_w, 0]
                            }
            n_steps_to_consider = (2 if self.extra_predictive_step else 1)
        else:
            weights_dict = {cognitive_module.get_a_specific_emotion('confident/frustrated').name: [default_w, 0, default_w],
                            cognitive_module.get_a_specific_emotion('interested/bored').name: [default_w, 0, default_w],
                            cognitive_module.get_a_specific_goal('quit game').name: [0, 0, 2*default_w],
                            cognitive_module.get_a_specific_goal('skip puzzle').name: [0, 0, 2*default_w],
                            cognitive_module.get_a_specific_belief('game difficulty').name: [0, 0, 2*default_w]
                            }
            n_steps_to_consider = self.n_horizon + (1 if self.extra_predictive_step else 0)
        cost = 0
        vars_in_cost = self.get_variables_that_affect_cost(weights_dict)
        for k in range(n_steps_to_consider):
            for var in vars_in_cost:
                var_value = var.values[-1 * n_steps_to_consider + k]
                var_value = max(min(var_value, 1), -1)
                if var.name == 'game difficulty' or var.name == 'change game difficulty':
                    cost += weights_dict[var.name][k] * abs(var_value)
                else:
                    cost += weights_dict[var.name][k] * var_value
        if self.verbose >= 3:
            aux_functions.print_some_vars(vars_in_cost)
        return cost

    def get_variables_that_affect_cost(self, weights_dict):
        """ returns the variables that affect the cost function, according to the weights dictionary

        Parameters
        ----------
        weights_dict : Dict[str, List[int]]

        Returns
        -------
        List[lib.tom_model.model_elements.variables.fst_dynamics_variables.Emotion]
        """
        vars_in_cost = []
        for key in weights_dict.keys():
            try:
                vars_in_cost.append(self.tom_model_predictive.cognitive_module.get_a_specific_emotion(key))
            except KeyError:
                try:
                    vars_in_cost.append(self.tom_model_predictive.cognitive_module.get_a_specific_goal(key))
                except KeyError:
                    vars_in_cost.append(self.tom_model_predictive.cognitive_module.get_a_specific_belief(key))
        return vars_in_cost

    def check_active_human_actions(self):
        """ check the actions of the participant that are active in the current moment

        Returns
        -------
        Dict[str, bool]
        """
        actions_dict = {}
        for action in self.tom_model_predictive.decision_making_module.action_selector.outputs:
            actions_dict[action.name] = action.active
        return actions_dict

    def check_constraints(self):
        """ assess whether the soft and hard constraints are violated if the current action is taken.
        Attention: To evaluate this, this method must be called after propagating the predictive model.

        Returns
        -------
        Tuple[bool, bool]
        """
        active_actions_dict = self.check_active_human_actions()
        return self.check_set_of_constraints(active_actions_dict, self.hard_constraints), \
               self.check_set_of_constraints(active_actions_dict, self.soft_constraints)

    def check_set_of_constraints(self, active_actions_dict, set_of_constraints):
        """ assess if a set of constraints is violated if the current action is taken.
        Attention: To evaluate this, this method must be called after propagating the predictive model.

        Parameters
        ----------
        active_actions_dict : Dict[str, bool]
        set_of_constraints : Union[List[str], List]

        Returns
        -------
        bool
        """
        for constraint in set_of_constraints:
            if active_actions_dict[constraint]:
                return False
        return True

    def set_all_actions(self):
        """ sets all the actions that the controller can choose from

        """
        for level in self.puzzle_difficulty_levels:
            for gr in self.give_reward_options:
                self.actions.append(RobotAction(level, gr))

    def load_model_parameters(self):
        """ loads the parameters of the perception, cognition, and decision-making modules in the main model and in the
        predictive model used by the controller

        """
        sheet_name = ('List of Parameters', )
        parameters_cog_df = excel_files.get_sheets_from_excel(None, input_file=self.file_cog, sheet_names=sheet_name)[0]
        parameters_dm_df = excel_files.get_sheets_from_excel(None, input_file=self.file_dm, sheet_names=sheet_name)[0]
        for model in (self.tom_model_predictive, self.tom_model):
            self.ided_vars, self.hidden_vars = \
                load_model.load_parameters_in_a_model(model, self.included_variables, self.id_config,
                                                      parameters_cog_df, parameters_dm_df)
            pass

    def ask_questions(self, puzzle_counter, mid_puzzle):
        """ poses the questions to the participant that allows to collect the current measures of the state variables
        (the mental states of the robot)

        Parameters
        ----------
        puzzle_counter : int
        mid_puzzle : bool

        Returns
        -------
        bool
        """
        if mid_puzzle:
            return self.questions_manager.is_time_to_ask_questions(puzzle_counter)
        return False

    def update_model_from_question(self, participant_answers):
        """ updates the values of the state variables of the model from the answers given by the participant

        Parameters
        ----------
        participant_answers : List[pandas.core.frame.DataFrame]
        """
        if self.id_config.simple_dynamics:
            self.update_model_from_question_simple_dyn(participant_answers)
        else:
            self.update_model_from_question_complex_dyn(participant_answers)

    def update_model_from_question_complex_dyn(self, participant_answers):
        """ updates the values of the state variables of the model from the answers given by the participant, when
        considering the complex dynamics of the model

        Parameters
        ----------
        participant_answers :
        """
        for var in self.ided_vars:          # update state vars from questions
            if participant_answers is not None:
                set_values_of_variables_cog.fill_values_of_variable(var, [participant_answers[-1]],
                                                                    self.id_config.simple_dynamics)
            elif self.for_interaction:
                print('\n My warning: NOT ABLE TO FILL VALUES FROM PARTICIPANTS ANSWERS!!!')
            var.value = var.values[-1]
            var.values.pop()
            var.values.extend([None, var.value])
        for var in self.hidden_vars:
            var.value = -1
            var.values.extend([None, var.value])
        for bias in self.tom_model.cognitive_module.get_biases():       # update biases from questions
            bias.values.append(bias.value)
        self.tom_model.cognitive_module.compute_and_update_biases()
        for bias in self.tom_model.cognitive_module.get_biases():
            bias.values.append(bias.value)
        for pk in get_rpks_of_model(self.tom_model):
            pk.values.extend([None, None])

    def update_model_from_question_simple_dyn(self, participant_answers):
        """ updates the values of the state variables of the model from the answers given by the participant, when
        considering the simplified dynamics of the model

        Parameters
        ----------
        participant_answers : List[pandas.core.frame.DataFrame]
        """
        for var in self.ided_vars:  # update state vars from questions
            if participant_answers is not None:
                set_values_of_variables_cog.fill_values_of_variable(var, [participant_answers[-1]],
                                                                    self.id_config.simple_dynamics)
            elif self.for_interaction:
                print('\n My warning: NOT ABLE TO FILL VALUES FROM PARTICIPANTS ANSWERS!!!')
            var.value = var.values[-1]
        for var in self.hidden_vars:
            var.value = -1
            var.values.append(var.value)
        self.tom_model.cognitive_module.compute_and_update_biases()
        for bias in self.tom_model.cognitive_module.get_biases():
            bias.values.append(bias.value)
        for rpk in get_rpks_of_model(self.tom_model):
            rpk.values.append(None)
        for pk in self.tom_model.cognitive_module.pk:
            pk.values.append(None)

    def set_next_action(self, action):
        """ set the variables that will enforce the choice of the next action (puzzle difficulty and give reward)

        Parameters
        ----------
        action : experimentNao.behaviour_controllers.robot_action.RobotAction

        Returns
        -------
        experimentNao.behaviour_controllers.robot_action.RobotAction
        """
        self.next_puzzle_difficulty = action.puzzle_difficulty_level
        self.give_reward_selected = action.give_reward
        return action

    def get_give_reward_status(self):
        """ communicates whether the controller has decided that Nao will give a reward or not

        Returns
        -------
        bool
        """
        return self.give_reward_selected

    def get_puzzle_difficulty_status(self):
        """ communicates the puzzle difficulty of the next puzzle, as decided by the controller

        Returns
        -------
        int
        """
        return self.next_puzzle_difficulty

    def print_values_of_computed_variables(self, verbose):
        """ prints the values of the variables that were computed to the console

        Parameters
        ----------
        verbose : int
        """
        if self.verbose > verbose:
            print_values_of_computed_variables(self.tom_model)

    def print_control_information(self, message: str):
        """ prints any generic output from the controller to the console

        Parameters
        ----------
        message : str
        """
        if self.verbose > 0:
            print(' [C]\t' + message)

    def print_actions(self, actions):
        """ prints the actions and their information to the controller

        Parameters
        ----------
        actions : List[experimentNao.behaviour_controllers.robot_action.RobotAction]
        """
        if self.verbose > 1:
            for action in actions:
                print(action.get_action_info(simple=False))
