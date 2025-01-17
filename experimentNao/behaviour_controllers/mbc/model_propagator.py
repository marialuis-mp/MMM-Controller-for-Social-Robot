from experimentNao.behaviour_controllers.mbc.aux_functions import print_values_of_computed_variables, \
    get_all_fast_dyn_vars
from experimentNao.data_analysis.pre_process_data import file_names
from experimentNao.declare_model import chess_interaction_data as cid
from experimentNao.model_ID.cognitive import set_values_of_variables_cog as set_values
from lib import excel_files


class ModelPropagation:
    def __init__(self, tom_model, predictive_model, rld, verbose, file_metrics, extra_predictive_step=False):
        """ Object that manages the propagation of the predictive model in order to allow assessing the consequences
        of taking certain actions into the future. Assumes complex dynamics.

        Parameters
        ----------
        tom_model :  experimentNao.declare_model.declare_entire_model.ToMModelChess
        predictive_model : experimentNao.declare_model.declare_entire_model.ToMModelChess
        rld : experimentNao.declare_model.modules.declare_perception_module.ChessRLD
        verbose : int
        file_metrics : pandas.io.excel._base.ExcelFile
        extra_predictive_step : bool
        """
        self.tom_model = tom_model
        self.rld = rld
        self.predictive_model = predictive_model
        self.verbose = verbose
        self.extra_predictive_step = extra_predictive_step
        self.rld_per_diff = None
        self.load_rld_per_diff(file_metrics)

    def update_model_w_n_horizon(self, u_minus_1, same_puzzle):
        """ updates the model twice (for n_horizon=2). It gets the previous u (u_minus_3) from the current rld and the
        current u (u_minus_1) as an argument. Then, it estimates the u in between (u_minus_2), and finally, calculates
        x_{k-1} using u_minus_2, and x_{k} using x_{k-1} and u_minus_1

        Parameters
        ----------
        u_minus_1 : experimentNao.declare_model.chess_interaction_data.ChessInteractionData
        same_puzzle : bool
        """
        u_minus_3 = self.rld.data if same_puzzle else set_values.get_a_data_point_for_start_of_puzzle(u_minus_1)
        u_minus_2 = cid.interpolate_between_two_points(u_minus_3, u_minus_1)
        self.print_control_input(u_minus_1, u_minus_2, u_minus_3)
        for u in (u_minus_2, u_minus_1):
            self.update_model_once(u)

    def update_model_for_action_selection(self, u_minus_1):
        """ updates the model once at the end of a puzzle, but before the action selection. This function should only be
        used when dealing with complex dynamics, because this update corresponds to an intermediate step between the
        last discrete time step and the current one, which only exists with complex dynamics. The model is updated with
        an interpolation between the current rld (k-1) and the last recorded rld (k-3), which results in u_{k-2}. The
        update with the current rld u_{k-1} is only done after the action is chosen.

        Parameters
        ----------
        u_minus_1 : experimentNao.declare_model.chess_interaction_data.ChessInteractionData
        """
        u_minus_3 = self.rld.data     # 1. Interpolate to get u_{k-2}
        u_minus_2 = cid.interpolate_between_two_points(u_minus_3, u_minus_1)
        self.print_control_input(u_minus_1, u_minus_2, u_minus_3)
        self.update_model_once(u_minus_2)           # 2. Run for x_{k-1} = f(x_{k-2}, u_{k-2})

    def run_predictive_model_w_action(self, action, u_minus_1):
        """ Propagates the predictive model with a certain action. First, it generates the correct u based on the
        potential new action, and then applies it to the model.

        Parameters
        ----------
        action : experimentNao.behaviour_controllers.robot_action.RobotAction
        u_minus_1 : experimentNao.declare_model.chess_interaction_data.ChessInteractionData
        """
        if self.verbose > 2:
            print('\n\tAction: {}\t{}'.format(action.give_reward, action.puzzle_difficulty_level))
        u_minus_1.nao_offering_rewards = action.give_reward         # 1. Set reward in u_{k-1}
        u_minus_1.reward_given = action.give_reward
        u_k = set_values.get_a_data_point_for_start_of_puzzle(u_minus_1)      # 2. Get in u_{k}
        u_k.puzzle_difficulty = action.puzzle_difficulty_level                # 2. Set reward in u_{k}
        inputs = (u_minus_1, u_k) if not self.extra_predictive_step else (u_minus_1, u_k, u_k)
        u_k.time_2_solve = self.rld_per_diff.iloc[action.puzzle_difficulty_level]['time_2_solve']
        u_k.n_wrong_attempts = [self.rld_per_diff.iloc[action.puzzle_difficulty_level]['n_wrong_attempts']]
        for u in inputs:
            update_a_model_once(self.predictive_model, u, compute_optimal_action=True)
        if self.verbose > 3:
            print_values_of_computed_variables(self.predictive_model)

    def update_model_once(self, u):
        """ updates the self.tom_model once with input u

        Parameters
        ----------
        u : experimentNao.declare_model.chess_interaction_data.ChessInteractionData
        """
        update_a_model_once(self.tom_model, u, False)

    def end_update_model_after_action_selection(self, action, u_minus_1):
        u_minus_1.nao_offering_rewards = action.give_reward
        u_minus_1.reward_given = action.give_reward
        self.update_model_once(u_minus_1)

    def print_control_input(self, u_m_1, u_m_2, u_m_3):
        """ prints the last three control inputs

        Parameters
        ----------
        u_m_1 : experimentNao.declare_model.chess_interaction_data.ChessInteractionData
            u_{k-1}
        u_m_2 : experimentNao.declare_model.chess_interaction_data.ChessInteractionData
            u_{k-2}
        u_m_3 : experimentNao.declare_model.chess_interaction_data.ChessInteractionData
            u_{k-3}
        """
        if self.verbose > 1:
            print(' [C]\tu_k-1: {}   u_k-2: {}   u_k-3: {}'.format(u_m_1.time_2_solve, u_m_2.time_2_solve, u_m_3.time_2_solve))

    def load_rld_per_diff(self, file_metrics):
        """ loads the real life data average values for each difficulty

        Parameters
        ----------
        file_metrics :
        """
        sheet_name = file_names.get_names_of_sheets(normalisation=False)
        self.rld_per_diff = excel_files.get_sheets_from_excel(None, [sheet_name], input_file=file_metrics)[0]


def update_a_model_once(tom_model, u, compute_optimal_action):
    """ this function updates the 'tom_model' using input 'u'

    Parameters
    ----------
    tom_model : experimentNao.declare_model.declare_entire_model.ToMModelChessSimpleDyn
    u : experimentNao.declare_model.chess_interaction_data.ChessInteractionData
    compute_optimal_action : bool
    """
    tom_model.perception_module.perceptual_access.inputs.set_data(u)
    tom_model.update_entire_model_in_1_go(compute_optimal_action=compute_optimal_action)
    for var in get_all_fast_dyn_vars(tom_model):
        var.values.append(var.value)
