import random

import path_config
from experimentNao.interaction import verbose
from lib import excel_files


class Puzzles:
    def __init__(self, lichess_db=True, interaction_number=None):
        self.lichess_db = lichess_db
        self.puzzles = []    # list of lists with puzzles; each list as puzzles with a different difficulty
        self.get_puzzles_from_file(interaction_number)
        # Not shown puzzles
        self.not_shown_puzzles = []
        self.set_not_shown_puzzles()

    def get_puzzles_from_file(self, interaction_number=None):
        path = path_config.repo_root / 'experimentNao' / 'chess_game'
        puzzles_dfs = excel_files.get_data_from_excel(path / ('all_puzzles.xlsx' if self.lichess_db else 'all_puzzles_old.xlsx'))
        for difficulty in range(len(puzzles_dfs)):
            self.puzzles.append([])             # add new list with a new difficulty to puzzles
            df = puzzles_dfs[difficulty]
            if interaction_number is not None:
                if interaction_number == 1 or interaction_number == 2:
                    df = df.head(100)
                elif interaction_number == 3:
                    df = df.iloc[100:200]
                elif interaction_number == 4:
                    df = df.iloc[200:300]
            for i in range(df.shape[0]):
                if self.lichess_db:
                    self.puzzles[difficulty].append(
                        ChessPuzzle(fen=df.at[i, 'FEN'], number_of_moves=int(df.at[i, 'N moves']),
                                    type_=df.at[i, 'Themes'], difficulty=difficulty, tag=i,
                                    sequence_of_moves=df.at[i, 'Moves'], url=df.at[i, 'PuzzleId']))
                else:
                    self.puzzles[difficulty].append(ChessPuzzle(fen=df.at[i, 'FEN'], number_of_moves=int(df.at[i, 'N moves']),
                                                                type_=df.at[i, 'Themes'], difficulty=difficulty, tag=i))

    def set_not_shown_puzzles(self):
        for i in range(len(self.puzzles)):
            self.not_shown_puzzles.append([i for i in range(0, len(self.puzzles[i]))])

    def get_new_random_puzzle(self, difficulty):
        puzzle2show = random.choice(self.not_shown_puzzles[difficulty])
        self.not_shown_puzzles[difficulty].remove(puzzle2show)
        return self.puzzles[difficulty][puzzle2show]


class ChessPuzzle:
    def __init__(self, fen, number_of_moves, difficulty, type_, tag=None, sequence_of_moves=None, url=None):
        self.fen = fen
        self.difficulty = difficulty
        self.type = type_
        self.number_of_moves = number_of_moves
        self.tag = tag
        self.sequence_of_moves = sequence_of_moves.split(' ') if sequence_of_moves is not None else sequence_of_moves
        self.url = url
