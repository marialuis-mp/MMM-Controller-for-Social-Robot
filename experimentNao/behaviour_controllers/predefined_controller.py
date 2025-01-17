from experimentNao.behaviour_controllers.controller import Controller


class PredefinedController(Controller):
    def __init__(self, max_number_of_puzzles, n_puzzles_per_group, session):
        """ This controller selects the action of the robot (experimentNao.behaviour_controllers.robot_action.RobotAction)
        as predefined for the training sessions, in order to generate the data required to identify the model.

        Parameters
        ----------
        max_number_of_puzzles : int
        n_puzzles_per_group : int
        session : int
        """
        super().__init__()
        if session == 1:
            self.difficulty_level = [0, 2, 4, 4, 2, 0]  # difficult of each group
        elif session == 2:
            self.difficulty_level = [5, 3, 1, 1, 3, 5]  # difficult of each group
        else:
            self.difficulty_level = [None] * 6
        self.nao_helping = True  # whether Nao helps in each group
        self.nao_offering_rewards = True
        self.number_of_puzzles_per_group = n_puzzles_per_group
        self.recommended_number_of_puzzles = len(self.difficulty_level) * self.number_of_puzzles_per_group
        # assert self.recommended_number_of_puzzles <= max_number_of_puzzles
        self.map = []       # saves the information of how many questions should be answered in each puzzle (0 if none)
        self.mapping(max_number_of_puzzles, max_number_of_puzzles, 0)

    def get_next_action(self, puzzle_counter, current_rld):
        """ decides the next action of the robot

        Parameters
        ----------
        puzzle_counter : int
        current_rld : experimentNao.declare_model.chess_interaction_data.ChessInteractionData
        """
        pass

    def get_characteristics_of_puzzle(self, current_puzzle, always_group_puzzles=True):
        """ gets the difficulty, whether nao is helping, and whether nao is giving rewards in the next puzzle.

        Parameters
        ----------
        current_puzzle : int
        always_group_puzzles : bool

        Returns
        -------
        Tuple[int, bool, bool]
        """
        if always_group_puzzles or (current_puzzle < self.recommended_number_of_puzzles):
            current_group = current_puzzle // self.number_of_puzzles_per_group
            while current_group >= len(self.difficulty_level):   # if we surpass the number of puzzles, repeat groups
                current_group -= len(self.difficulty_level)
        else:
            print(' [C]\tSurpassed recommended puzzle numbers: {}', self.recommended_number_of_puzzles)
            current_group = current_puzzle % self.recommended_number_of_puzzles
        current_difficulty = self.difficulty_level[current_group]
        return current_difficulty, self.nao_helping, self.nao_offering_rewards

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
        return self.map[puzzle_counter]

    # When to ask questions in puzzle
    def mapping(self, n_puzzles, n_puzzles_with_questions, n_puzzles_without_questions):
        """ sets whether feedback questions will be asked in each puzzle to be played, puzzle by puzzle.
        Sets this information in self.map, in which self.map is an array with as many elements as the number of puzzles
        to be played. Element i contains if feedback questions should be asked in the $i^th$ puzzle to be played.

        Parameters
        ----------
        n_puzzles : int
        n_puzzles_with_questions : int
            number of puzzles in a row with questions
        n_puzzles_without_questions : int
            number of puzzles in a row without questions

        """
        while len(self.map) < n_puzzles:     # add elements in the right sequence (X with puzzles, Y without)
            self.map.extend([True]*n_puzzles_with_questions)        # X: n_puzzles_with_questions
            self.map.extend([False]*n_puzzles_without_questions)    # Y: n_puzzles_without_questions
        while len(self.map) > n_puzzles:   # since we added puzzles in groups of X + Y, remove last elements that
            self.map.pop()                      # surpass the number of puzzles, so that the self.map has right length
