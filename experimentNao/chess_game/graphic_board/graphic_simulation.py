import time
from lib.util import Point
from experimentNao.chess_game.graphic_board import graphic_chess_board as gcb, graphic_main_window


class GraphicSimulation:
    def __init__(self, my_chess_engine, participant_requests, interaction_mode=False, second_screen=False, counter=0):
        self.chess_engine = my_chess_engine
        self.participant_requests = participant_requests
        chess_board_size = 1000
        self.window_size = Point(1900, chess_board_size)
        self.board_canvas_size = Point(chess_board_size, chess_board_size)
        self.main_window = graphic_main_window.MainWindowChess(self.window_size, self.board_canvas_size,  center=False,
                                                               screen_number=(1 if second_screen else None))
        self.graphic_chess_board = None
        self.interaction_mode = interaction_mode
        self.microphone_needs_reset = False
        self.counter = counter
        self.main_window.update()

    def show_board_ask_for_move(self, current_move, last_move):
        """

        Parameters
        ----------
        current_move : int
            number of the current move (1st move of puzzle is 0)
        last_move : bool
            whether this is the last move
        """
        if current_move == 0:  # if it is the first move - start simulation
            self.start_simulation(last_move)
        else:
            self.resume_simulation(last_move)

    def start_simulation(self, last_move):
        self.main_window.add_canvas(self.board_canvas_size)
        self.main_window.draw_side_panel(self.chess_engine, self.counter, button_request_command=self.check_for_requests,
                                         button_mic_command=self.flag_that_mic_needs_reset)
        self.graphic_chess_board = gcb.GraphicChessBoard(self.chess_engine, self.board_canvas_size.x, self.main_window)
        self.draw_initial_board()
        if not self.interaction_mode:
            self.run_simulation(last_move)

    def draw_initial_board(self):
        if self.chess_engine.lichess_db:
            first_opponent_move = self.chess_engine.current_puzzle.sequence_of_moves[0]
            self.graphic_chess_board.draw_pieces_before_1st_move_from_board_engine(first_opponent_move)
            self.graphic_chess_board.highlight_move(first_opponent_move, color='blue')
            self.graphic_chess_board.delete_highlights(time_=1)
            self.graphic_chess_board.re_draw_board()
        else:
            self.graphic_chess_board.draw_pieces_from_board_engine()

    def resume_simulation(self, last_move):
        self.main_window.replace_instruction_in_side_screen('Choose your best move!')
        # self.graphic_chess_board.re_draw_board()
        self.main_window.update()                                               # Show board and previous highlights
        self.graphic_chess_board.delete_highlights(show_immediately=True)       # Remove highlights and show it
        if not self.interaction_mode:
            self.run_simulation(last_move)                              # Run simulation again

    def run_simulation(self, last_move):
        while not self.chess_engine.move_chosen:
            self.main_window.update()
        if last_move:
            self.finish_puzzle_simulation()

    def run_simulation_interaction_mode(self):
        self.main_window.update()

    def finish_puzzle_simulation(self):
        self.main_window.replace_instruction_in_side_screen('You solved the puzzle!')
        self.main_window.update()
        self.main_window.root.after(1500, self.main_window.clear_window())
        self.main_window.update()

    def run_computer_move(self, computer_move):
        self.graphic_chess_board.highlight_move(computer_move)
        self.graphic_chess_board.re_draw_board()
        self.main_window.root.after(100, self.main_window.update())

    def set_counter(self, counter):
        self.counter = counter

    def flag_that_mic_needs_reset(self):
        self.microphone_needs_reset = True

    def check_for_requests(self):
        self.participant_requests.request_graphic_check_in_progress = True
        self.main_window.show_request_options(self.participant_requests.get_requests(), self.confirm_request)
        while self.participant_requests.request_graphic_check_in_progress:
            self.main_window.update()
        self.main_window.remove_canvas()
        self.main_window.update()

    def confirm_request(self, request_id):
        if request_id is not None:
            request = self.participant_requests.get_requests()[request_id]
            request.participant_wants_it = self.main_window.ask_question('Please confirm', request.question_default)
        self.participant_requests.request_graphic_check_in_progress = False
