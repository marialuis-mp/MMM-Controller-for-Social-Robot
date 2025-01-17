import math
import time
import pandas as pd
from experimentNao.declare_model.chess_interaction_data import ChessInteractionData

from lib import excel_files


class PerformanceIndicators:
    def __init__(self):
        """ object that holds the indicators of the performance of the participant in the game, which also correspond
        to the inputs of the ToM model

        """
        self.indicators = ChessInteractionData()
        # auxiliary variables
        self.start_time = 0
        self.n_moves_revealed = 0
        self.times_spent_in_questions = []
        self.columns_output = ('Step', ) + self.indicators.df_columns + ('Quit', )
        self.columns_df_puzzle_list = ('Puzzle number', 'difficulty', 'fen')
        self.df = pd.DataFrame(columns=self.columns_output)
        self.df_puzzle_list = pd.DataFrame(columns=self.columns_df_puzzle_list)
        self.writer = None
        self.n_times_data_saved_in_puzzle = 0

    def reset_performance_indicators(self):
        """ resets all performance indicators

        """
        self.indicators.reset_data()
        self.start_time = time.time()
        self.n_moves_revealed = 0
        self.times_spent_in_questions = []
        self.n_times_data_saved_in_puzzle = 0

    def save_number_wrong_moves_in_turn(self, chess_engine):
        """ saves the number of wrong moves that were performed in the current move

        Parameters
        ----------
        chess_engine : experimentNao.chess_game.my_chess_engine.MyChessEngine
        """
        self.indicators.n_wrong_attempts.append(chess_engine.number_wrong_attempts_in_move)

    def save_and_write_indicators(self, chess, current_puzzle_number, helping_system, reward_system, skipped_puzzle,
                                  quit_game):
        """ saves the indicators and writes them to excel

        Parameters
        ----------
        chess : experimentNao.chess_game.my_chess_engine.MyChessEngine
        current_puzzle_number : int
        helping_system : experimentNao.interaction.nao_behaviour.hints.HelpingSystem
        reward_system : experimentNao.interaction.nao_behaviour.reward_system.RewardSystemScheduled
        skipped_puzzle : bool
        quit_game : bool
        """
        self.save_indicators(chess, helping_system, reward_system, skipped_puzzle)
        self.write_indicators_2_excel(current_puzzle_number, quit_game)

    def save_indicators(self, chess, helping_system, reward_system, skipped):
        """ save indicators at the current moment

        Parameters
        ----------
        chess : experimentNao.chess_game.my_chess_engine.MyChessEngine
        helping_system : experimentNao.interaction.nao_behaviour.hints.HelpingSystem
        reward_system : experimentNao.interaction.nao_behaviour.reward_system.RewardSystemScheduled
        skipped : bool
        """
        time_taken = time.time() - self.start_time - sum(self.times_spent_in_questions)
        n_moves_ttl = math.ceil(chess.current_puzzle.number_of_moves / 2)
        self.indicators.fill_data(puzzle_difficulty=chess.current_puzzle.difficulty,
                                  time_2_solve=time_taken,
                                  prop_moves_revealed=self.n_moves_revealed / n_moves_ttl,
                                  nao_helping=helping_system.nao_helping,
                                  nao_offering_reward=reward_system.nao_offering_rewards,
                                  skipped=skipped)

    def write_indicators_2_excel(self, current_puzzle_number, quit_game):
        """ writes the object to the Excel file

        Parameters
        ----------
        current_puzzle_number : int
        quit_game : bool
        """
        index_name = current_puzzle_number + 0.1 * self.n_times_data_saved_in_puzzle   # puzzle.save_number
        to_add = pd.DataFrame(data=[[index_name] + self.indicators.get_as_array() + [quit_game]],
                              columns=self.columns_output)
        self.df = pd.concat([self.df, to_add])
        excel_files.save_df_to_excel_sheet(self.writer, self.df, 'Performance')
        self.n_times_data_saved_in_puzzle += 1

    def hint_given(self):
        """ updates 'n_hints' indicator when a hint is given

        """
        self.indicators.n_hints += 1

    def move_revealed(self):
        """ updates 'n_moves_revealed' indicator when a move is revealed

        """
        self.n_moves_revealed += 1

    def set_excel(self, writer_file):
        """ sets the Excel as self.writer at the beginning of the interaction

        """
        self.writer = writer_file

    def save_puzzle_info(self, puzzle):
        """ save the indicators of the puzzle, at the end of the puzzle, to the Excel file

        Parameters
        ----------
        puzzle : experimentNao.chess_game.chess_puzzles.ChessPuzzle
        """
        to_add = pd.DataFrame(data=[[puzzle.tag, puzzle.difficulty, puzzle.fen]], columns=self.columns_df_puzzle_list)
        self.df_puzzle_list = pd.concat([self.df_puzzle_list, to_add])
        excel_files.save_df_to_excel_sheet(self.writer, self.df_puzzle_list, 'Puzzle list')
