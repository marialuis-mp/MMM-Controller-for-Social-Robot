import math


class TimeStepsMapping:
    def __init__(self, prediction_horizon):
        """ Maps when there are discrete time steps in the interaction

        Parameters
        ----------
        prediction_horizon : int
        """
        self.prediction_horizon = prediction_horizon

    def when_are_time_steps_of_puzzle(self, n_moves):
        """ Returns the moves (in integers) that correspond to a time step. If the number of moves of the selected
        puzzle does not allow to ask the necessary amount of questions pre-defined for the next puzzle, None is returned.
        This is done by checking if the number of moves of the puzzle that are to be played by the player is smaller
        than the number of questions that need to be asked.

        Parameters
        ----------
        n_moves : int
            number of moves of the puzzle that was randomly selected to be played next

        Returns
        -------
        Union[None, List[int]]
        """
        n_questions = self.prediction_horizon
        if (n_moves + 1) / n_questions < 2:
            return None
        moves_to_ask_quest = []
        frequency_questions = n_moves / n_questions
        for i in range(1, n_questions):     # equally distribute the questions throughout the moves
            when2ask = math.floor(i*frequency_questions) - 1
            moves_to_ask_quest.append(when2ask if (when2ask % 2) == 0 else when2ask - 1)    # round it to lower odd numb
        moves_to_ask_quest.append(n_moves - 1)
        return moves_to_ask_quest

