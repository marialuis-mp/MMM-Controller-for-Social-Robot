from stockfish import Stockfish
import chess

from experimentNao.chess_game import chess_puzzles
from experimentNao.chess_game.graphic_board import graphic_simulation
from experimentNao.folder_path import stockfish_path


class MyChessEngine:
    def __init__(self, current_difficulty=0, interaction_mode=False, lichess_db=True, interaction_number=None):
        """ my chess engine that combines stockfish and the chess packages. It is optimized to play puzzles.

        Parameters
        ----------
        current_difficulty : int
            current difficulty of the puzzle
        interaction_mode : bool
            whether we are in interaction mode (for participants) where a graphic board is presented
        """
        self.path = stockfish_path + "/stockfish_15.1_win_x64_avx2/stockfish-windows-2022-x86-64-avx2"
        # Engines
        self.stockfish = Stockfish(path=self.path, depth=18, parameters={"Threads": 2, "Minimum Thinking Time": 30})
        self.board = chess.Board()
        self.lichess_db = lichess_db
        # Puzzles
        self.puzzles = chess_puzzles.Puzzles(lichess_db, interaction_number)
        self.current_puzzle = None
        self.current_move_in_puzzle = 0
        self.current_difficulty = current_difficulty
        # Current game variables
        self.current_fen = None
        self.computer_color_white = None
        self.current_player_legal_moves = []
        self.move_chosen = False                        # did player choose the move
        self.ideal_move = None
        self.number_wrong_attempts_in_move = None       # for puzzle
        self.opponent_next_move, self.user_next_move = None, None
        self.piece_taken_before_puzzle_start = None
        # Function and objects used to display board
        self.graphic_simulation = None
        self.display_function = None    # function to display board: default is 'show_board_ask_for_move()'
        if not interaction_mode:
            self.set_graphic_simulation(graphic_simulation.GraphicSimulation(self))
            self.display_function = lambda current_move, last_move: \
                self.graphic_simulation.show_board_ask_for_move(current_move, last_move)
            self.display_engine_best_move = lambda best_move: self.graphic_simulation.run_computer_move(best_move)

    def set_new_puzzle(self):
        """ sets the puzzle to be played next

        """
        self.current_puzzle = self.puzzles.get_new_random_puzzle(self.current_difficulty)
        self.set_new_board_position(self.current_puzzle.fen)
        if self.lichess_db:
            first_move = self.current_puzzle.sequence_of_moves[0]
            self.piece_taken_before_puzzle_start = self.stockfish.get_what_is_on_square(first_move[2:4])
            self.stockfish.make_moves_from_current_position([first_move])  # Make move in stockfish
            self.set_new_board_position(self.stockfish.get_fen_position())  # Set board position in chess
            self.current_player_legal_moves = self.board.legal_moves
        # Initialize relevant variables
        self.computer_color_white = not self.is_next_player_white()
        self.current_player_legal_moves = []
        self.current_move_in_puzzle = 0

    def run_puzzle(self, select_puzzle=True):
        """ runs a new puzzle: gets a puzzle from the database, and runs it for the right amount of moves.

        """
        if select_puzzle:
            self.set_new_puzzle()
        while self.current_move_in_puzzle < self.current_puzzle.number_of_moves:
            self.manage_next_move()

    def manage_next_move(self):
        """ ask for the next move of the player or apply best move of the computer, depending on whose turn it is to
        play. It does not have to be played in the puzzle. Can be used to play a normal game

        """
        if self.is_humans_turn():
            if self.lichess_db:
                self.user_next_move = self.current_puzzle.sequence_of_moves[self.current_move_in_puzzle + 1]
            self.ask_for_next_player_move()
        else:
            if self.lichess_db:
                self.opponent_next_move = self.current_puzzle.sequence_of_moves[self.current_move_in_puzzle + 1]
                self.apply_move(self.opponent_next_move)
                self.display_engine_best_move(self.opponent_next_move)
            else:
                self.opponent_next_move = self.get_and_apply_best_move()
        self.current_move_in_puzzle += 1

    def set_new_board_position(self, new_fen_position):
        """ sets the board position to a new 'new_fen_position'

        Parameters
        ----------
        new_fen_position : str
        """
        self.stockfish.is_fen_valid(new_fen_position)           # Make sure fen is valid
        self.current_fen = new_fen_position
        self.board = chess.Board(self.current_fen)          # Set board position in chess
        self.stockfish.set_fen_position(new_fen_position)       # Set fen position in stockfish

    def get_and_apply_best_move(self):
        """ get the best move from stockfish and apply it to the board

        """
        best_move = self.stockfish.get_best_move()
        self.apply_move(best_move)
        self.display_engine_best_move(best_move)
        return best_move

    def apply_move(self, move):
        """ applies a move to the board

        Parameters
        ----------
        move : chess.Move
        """
        self.stockfish.make_moves_from_current_position([move])                # Make move in stockfish
        self.set_new_board_position(self.stockfish.get_fen_position())    # Set board position in chess
        self.current_player_legal_moves = self.board.legal_moves
        self.move_chosen = True

    def ask_for_next_player_move(self):
        """ prepares engined for the player's next move and asks the player for their next move.

        """
        self.number_wrong_attempts_in_move = 0
        self.set_ideal_move()
        self.move_chosen = False
        last_move = True if self.current_move_in_puzzle == (self.current_puzzle.number_of_moves - 1) else False
        self.display_function(self.current_move_in_puzzle, last_move)

    def is_next_player_white(self):
        """ whether the next turn is to be played by the player who is playing with the white or black pieces.

        Returns
        -------
        bool
        """
        if ' w ' in self.stockfish.get_fen_position():
            return True
        else:
            return False

    def is_humans_turn(self):
        """ return true if currently it is the human's turn to play; returns false if it is the computer's turn to play

        Returns
        -------

        """
        return not (self.is_next_player_white() == self.computer_color_white)

    def set_graphic_simulation(self, graphic_simulation_):
        """

        Parameters
        ----------
        graphic_simulation_ : experimentNao.chess_game.graphic_board.graphic_simulation.GraphicSimulation
        """
        self.graphic_simulation = graphic_simulation_

    def set_function_that_shows_board_and_asks_for_move(self, function_):
        """ sets the function that manages the interface where the board is shown to the users and where users can
        apply also their move. The display function is called when the board is presented to the users in order to get
        the user's chosen move

        Parameters
        ----------
        function_ : function
        """
        self.display_function = function_

    def set_function_that_displays_computers_move(self, function_):
        """ sets the function that shows the move chosen by the computer through the interface where the board is shown
        to the users. The display function is called when it is the computer's turn and it choses the best move.

        Parameters
        ----------
        function_ : function
        """
        self.display_engine_best_move = function_

    def set_ideal_move(self):
        """ sets the ideal move of the player, to be compared with the player choice

        Parameters
        ----------
        """
        if self.lichess_db:
            self.ideal_move = self.user_next_move
        else:
            self.ideal_move = self.stockfish.get_best_move()

    def get_positions_of_ideal_move(self):
        """ converts the ideal move into the positions that are part of the move (position where the moved piece is and
        the position )

        Returns
        -------
        Tuple[str, str]
        """
        return self.ideal_move[0:2], self.ideal_move[2:4]

    @staticmethod
    def get_positions_of_move(move):
        """ converts a move into the positions that are part of the move (position where the moved piece is and
        the position )

        Parameters
        ----------
        move : str

        Returns
        -------

        """
        return move[0:2], move[2:4]

    def piece_in_position(self, position: str):
        """ returns the object and the name of the piece in the position received as parameter

        Parameters
        ----------
        position : str

        Returns
        -------
        Tuple[chess.Piece, str]
        """
        piece = self.board.piece_at(chess.parse_square(position))
        if piece is None:
            return None, None
        name_of_piece = chess.piece_name(piece.piece_type)
        return piece, name_of_piece

    def get_location_of_piece(self, piece, color):
        """ returns the location of the piece of the color received as parameter. if there are more than one piece that
        satisfies the conditions, only the first is returned. todo: return all location of pieces that fulfil requirement

        Parameters
        ----------
        piece : str
            identifying letter of the piece (e.g., 'p' for pawn, 'q' for queen, 'k' for king', 'n' for night, )
        color : str
            'b' for black, and 'w' for white

        Returns
        -------
        str
        """
        board_str = str(self.board)
        char_of_piece = piece.upper() if color == 'w' else piece.lower()
        i, j = 0, 0
        for char in board_str:
            if char == char_of_piece:
                break
            elif char == ' ':
                i += 1
            elif char == '\n':
                i = 0
                j += 1
        return 'abcdefgh'[i] + str(8-j)

    def show_board(self):
        """ show board on the console

        """
        print(self.board)
