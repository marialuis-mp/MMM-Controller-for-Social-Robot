from abc import ABC, abstractmethod

from experimentNao.behaviour_controllers.time_steps_mapping import TimeStepsMapping


class Controller(ABC):
    def __init__(self):
        """ Parent class of the controller that steer the behaviour of the robot. The controller should decide, after
        each puzzle the difficulty of the next puzzle and whether to give a reward to the participant.

        """
        self.puzzle_difficulty_levels = [0, 1, 2, 3, 4, 5]
        self.give_reward_options = [False, True]
        self.time_steps_mapping = TimeStepsMapping(2)
        # Time steps
        self.when_are_time_steps_in_puzzle = []

    @abstractmethod
    def get_next_action(self, puzzle_counter, current_rld):
        """ decides the next action of the robot

        Parameters
        ----------
        puzzle_counter : int
        current_rld : experimentNao.declare_model.chess_interaction_data.ChessInteractionData
        """
        pass

    @abstractmethod
    def ask_questions(self, puzzle_counter, mid_puzzle):
        """ poses the questions to the participant that allows to collect the current measures of the state variables
        (the mental states of the robot)

        Parameters
        ----------
        puzzle_counter : int
        mid_puzzle : bool
        """
        pass

    def reset_beginning_of_puzzle(self, n_moves):
        """ Resets all the information of the object before a new puzzle is played. If the number of moves of selected
        puzzle is too small to ask the number of questions that should be asked in this puzzle, then 'False' is returned.

        Parameters
        ----------
        n_moves : int
            number of moves of the puzzle that was randomly selected to be played next

        Returns
        -------
        bool
        """
        self.when_are_time_steps_in_puzzle = self.time_steps_mapping.when_are_time_steps_of_puzzle(n_moves)
        return self.when_are_time_steps_in_puzzle is not None

    def check_if_it_is_discrete_time_step(self, current_move):
        """ check if the current move of the players coincides with a discrete time step of our controller

        Parameters
        ----------
        current_move : int

        Returns
        -------

        """
        if current_move in self.when_are_time_steps_in_puzzle:  # 2. in this move
            return True

