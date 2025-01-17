from experimentNao.behaviour_controllers.mbc import model_propagator


class ModelPropagationSimple(model_propagator.ModelPropagation):
    def __init__(self, tom_model, predictive_model, rld, verbose, file_metrics, extra_predictive_step=False):
        """ Object that manages the propagation of the predictive model in order to allow assessing the consequences
        of taking certain actions into the future. Assumes simplified dynamics.

        Parameters
        ----------
        tom_model : experimentNao.declare_model.declare_entire_model.ToMModelChessSimpleDyn
        predictive_model : experimentNao.declare_model.declare_entire_model.ToMModelChessSimpleDyn
        rld : experimentNao.declare_model.modules.declare_perception_module.ChessRLD
        verbose : int
        file_metrics : pandas.io.excel._base.ExcelFile
        extra_predictive_step : bool
        """
        super().__init__(tom_model, predictive_model, rld, verbose, file_metrics, extra_predictive_step)

    def update_model_w_n_horizon(self, u_minus_1, same_puzzle):
        """ updates the model (for n_horizon=1). It gets the previous u (u_minus_2) from the current rld and the
        current u (u_minus_1) as an argument. Then, it  calculates x_{k-1} using u_minus_2, and x_{k} using u_minus_1

        Parameters
        ----------
        u_minus_1 : experimentNao.declare_model.chess_interaction_data.ChessInteractionData
        same_puzzle : bool
        """
        u_minus_2 = self.rld.data
        self.print_control_input(u_minus_1, u_minus_2, None)
        self.update_model_once(u_minus_1)

    def update_model_for_action_selection(self, u_minus_1):
        pass    # no need to update model before action selection, because of simplified dynamics


    def print_control_input(self, u_m_1, u_m_2, u_m_3):
        """ prints the last three control inputs

        Parameters
        ----------
        u_m_1 : experimentNao.declare_model.chess_interaction_data.ChessInteractionData
        u_m_2 : experimentNao.declare_model.chess_interaction_data.ChessInteractionData
        u_m_3 : experimentNao.declare_model.chess_interaction_data.ChessInteractionData
        """
        if self.verbose > 1:
            print(' [C]\tu_k-2: {}   u_k-1: {}'.format(u_m_2.time_2_solve, u_m_1.time_2_solve))
