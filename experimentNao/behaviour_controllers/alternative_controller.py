import copy
import random
import time
from enum import Enum

from experimentNao.behaviour_controllers.mbc import model_based_controller
from experimentNao.data_analysis.pre_process_data import file_names
from experimentNao.participant import participant_identifier
from lib import excel_files


class AlternativeController(model_based_controller.ModelBasedController):
    def __init__(self, id_config, session_time, verbose):
        """  model-free controller used in the third session as a baseline, to compare with the model-based controller

        Parameters
        ----------
        id_config : experimentNao.model_ID.configs.overall_config.IDConfig
        session_time : int
        verbose : int
        """
        self.session_time = session_time     # in seconds
        mode = DifficultyDistributionModes.RANDOM
        self.changing_diff_mode = MoveToNextDiffModes.TIME
        # set mode of sorting difficulties
        self.possible_difficulties = list(range(6))
        self.difficulty_groups = []
        self.current_group = 0
        self.set_difficulty_groups(mode)
        self.difficulty_groups = [5, 3, 1, 0, 2, 4]
        # Set mode of changing to next difficulty
        if self.changing_diff_mode == MoveToNextDiffModes.TIME:
            self.times_to_change_diff = []
            self.starting_time = time.time()
            self.set_times_to_change_diff()
        else:
            self.n_puzzles_per_group = []
            self.set_number_of_puzzles_per_diff()
            print('\t[AC] n_puzzles_per_diff', self.n_puzzles_per_group)
        # Give reward probability
        self.reward_probability = 1/3
        super().__init__(id_config, verbose)

    def initialize_controller(self, puzzle_difficulty, nao_helping, nao_offering_reward):
        """ initializes the variables of the controller

        Parameters
        ----------
        puzzle_difficulty : int
        nao_helping : bool
        nao_offering_reward : bool
        """
        super().initialize_controller(self.difficulty_groups[0], nao_helping, nao_offering_reward)

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
        if self.is_it_time_to_change_diff_group(puzzle_counter):
            self.current_group += 1
        difficulty = self.difficulty_groups[min(self.current_group, len(self.difficulty_groups)-1)]
        reward = random.random() < self.reward_probability
        return next((a for a in self.actions if a.puzzle_difficulty_level == difficulty and a.give_reward == reward))

    def set_difficulty_groups(self, mode):
        """ generate the difficulty groups depending on the mode of sorting the difficulties

        Parameters
        ----------
        mode : experimentNao.behaviour_controllers.alternative_controller.DifficultyDistributionModes
        """
        self.difficulty_groups = []
        if mode == DifficultyDistributionModes.ASCENDING:
            for i in self.possible_difficulties:
                self.difficulty_groups = copy.copy(self.possible_difficulties)
        elif mode == DifficultyDistributionModes.DESCENDING:
            for i in reversed(self.possible_difficulties):
                self.difficulty_groups = copy.copy(self.possible_difficulties)
                self.difficulty_groups = self.difficulty_groups[::-1]
        elif mode == DifficultyDistributionModes.AVERAGE:
            self.difficulty_groups = [3, 2, 3, 2, 3, 2]
        elif mode == DifficultyDistributionModes.RANDOM:
            difficulties_copy = copy.copy(self.possible_difficulties)
            random.shuffle(difficulties_copy)
            self.difficulty_groups = difficulties_copy
        print(self.difficulty_groups)

    def set_number_of_puzzles_per_diff(self):
        """ sets how many puzzle should be played per difficulty
        (for when changing_diff_mode == MoveToNextDiffModes.COUNTER)

        """
        path = file_names.get_name_of_metric_file_2_read(participant_identifier)
        df = excel_files.get_sheets_from_excel(path, sheet_names=['RLD metrics per diff'])[0]
        avg_times = list(df['time_2_solve'])
        util_time = self.session_time * 0.9
        time_per_group = util_time / len(self.possible_difficulties)
        for diff in self.difficulty_groups:
            avg_time = avg_times[diff] + 10     # 10 seconds for start and end of puzzle
            self.n_puzzles_per_group.append(time_per_group // avg_time)

    def set_times_to_change_diff(self):
        """ sets the times, in seconds, from the beginning of the interaction, when the difficulty should be switched
        for the next one (for when changing_diff_mode == MoveToNextDiffModes.TIME)

        """
        time_per_group = self.session_time / len(self.possible_difficulties)
        for i in range(len(self.possible_difficulties)):
            self.times_to_change_diff.append((1+i)*time_per_group - time_per_group/10)
        self.times_to_change_diff[-1] = self.session_time   # prevent bugs
        print('\t[AC] Times to change diff:', self.times_to_change_diff)

    def is_it_time_to_change_diff_group(self, puzzle_counter):
        """ checks whether it is time to change difficulty group
        (for when changing_diff_mode == MoveToNextDiffModes.TIME)

        Parameters
        ----------
        puzzle_counter : int

        Returns
        -------
        bool
        """
        if self.changing_diff_mode == MoveToNextDiffModes.TIME:
            time_elapsed = time.time() - self.starting_time
            print('Time elapsed {}\t'.format(time_elapsed))
            if time_elapsed > self.times_to_change_diff[self.current_group]:
                print('Time to change {}'.format(self.times_to_change_diff[self.current_group]))
                return True
            return False
        else:
            if puzzle_counter > sum(self.n_puzzles_per_group[:self.current_group]):
                return True
            return False


class DifficultyDistributionModes(Enum):
    RANDOM = 1
    ASCENDING = 2
    DESCENDING = 3
    AVERAGE = 4


class MoveToNextDiffModes(Enum):
    COUNTER = 1
    TIME = 2