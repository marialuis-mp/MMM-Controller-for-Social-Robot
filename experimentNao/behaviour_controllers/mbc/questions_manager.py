import time


class QuestionsManagerMBC:
    def __init__(self, puzzle_periodic_questions: bool, time_periodic_questions: bool):
        """ manages the questions asked to the participant for the MBC

        Parameters
        ----------
        puzzle_periodic_questions : bool
        time_periodic_questions : bool
        """
        self.question_to_initialize = True
        self.puzzle_periodic_questions = puzzle_periodic_questions
        self.time_periodic_questions = time_periodic_questions
        # Set managing variables
        if self.question_to_initialize or self.time_periodic_questions or self.puzzle_periodic_questions:
            self.update_w_values_from_question = True
            self.already_asked_in_puzzle = False
            if self.puzzle_periodic_questions:
                self.periodicity_of_questions_in_puzzles = 3
                self.puzzle_counter_of_last_question = 0
            if self.time_periodic_questions:
                self.periodicity_of_questions_in_time = 150
                self.time_of_last_question = 0
        else:
            self.update_w_values_from_question = False

    def is_time_to_ask_questions(self, puzzle_counter):
        """ checks whether in the current discrete time step the questions regarding the mental states should be asked
        to the participant, depending on the different criteria

        Parameters
        ----------
        puzzle_counter : int

        Returns
        -------
        bool
        """
        if self.is_time_to_ask_questions_initialization(puzzle_counter):
            self.update_values_when_question_is_asked(puzzle_counter)
            return True
        if self.is_time_to_ask_questions_puzzle_periodic(puzzle_counter):
            self.update_values_when_question_is_asked(puzzle_counter)
            return True
        if self.is_time_to_ask_questions_time_periodic():
            self.update_values_when_question_is_asked(puzzle_counter)
            return True
        return False

    def is_time_to_ask_questions_initialization(self, puzzle_counter):
        """ checks whether in the current discrete time step the questions regarding the mental states should be asked
        to the participant, due to the purpose of initializing the model (at the beginning of the interaction)

        Parameters
        ----------
        puzzle_counter : int

        Returns
        -------
        bool
        """
        if self.question_to_initialize and puzzle_counter == 0:
            if not self.already_asked_in_puzzle:
                return True
        return False

    def is_time_to_ask_questions_puzzle_periodic(self, puzzle_counter):
        """ checks whether in the current discrete time step the questions regarding the mental states should be asked
        to the participant, due to the fact that enough puzzles passed since the last question

        Parameters
        ----------
        puzzle_counter : int

        Returns
        -------

        """
        if self.puzzle_periodic_questions:
            number_of_puzzles_elapsed = puzzle_counter - self.puzzle_counter_of_last_question
            if number_of_puzzles_elapsed >= self.periodicity_of_questions_in_puzzles:
                if not self.already_asked_in_puzzle:
                    print('\t[C] Question asked due to puzzle periodicity')
                    return True
        return False

    def is_time_to_ask_questions_time_periodic(self):
        """ checks whether in the current discrete time step the questions regarding the mental states should be asked
        to the participant, due to the fact that enough time passed since the last question

        Returns
        -------

        """
        if self.time_periodic_questions:
            time_elapsed = time.time() - self.time_of_last_question
            if time_elapsed > self.periodicity_of_questions_in_time:
                print('\t[C] Question asked due to time')
                return True
        return False

    def update_values_when_question_is_asked(self, puzzle_counter):
        """ updates the flags that trigger asking the questions once the questions were just asked

        Parameters
        ----------
        puzzle_counter : int
        """
        self.update_w_values_from_question = True
        self.already_asked_in_puzzle = True
        if self.time_periodic_questions:
            self.time_of_last_question = time.time()
            self.puzzle_counter_of_last_question = puzzle_counter

    def update_after_question_was_asked(self):
        """ updates flag after the questions were just asked

        """
        self.update_w_values_from_question = False

    def reset_beginning_of_puzzle(self):
        """ resets flag at beginning of the puzzle

        """
        self.already_asked_in_puzzle = False
