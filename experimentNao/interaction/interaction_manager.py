import sys
import time
import random
from enum import Enum

from experimentNao import folder_path
from lib.speech_recognition_module import my_speech_recognition as sr
from lib import excel_files
from experimentNao.declare_model import declare_entire_model as dem
from experimentNao.behaviour_controllers import predefined_controller as pc, alternative_controller as ac
from experimentNao.behaviour_controllers.mbc import model_based_controller as mbc
from experimentNao.interaction import verbose
from experimentNao.interaction.performance_of_participant import performance_indicators as pi, \
    participant_feedback as parti_fb
from experimentNao.interaction.nao_behaviour import conversation_manager as convo, nao_requests, reward_system as rs, \
    hints, participant_requests
from experimentNao.chess_game import my_chess_engine
from experimentNao.chess_game.graphic_board import graphic_simulation as g_sim


class Interaction:
    def __init__(self, interaction_settings, id_conf):
        """ Manages the interaction between Nao and the human participant. It brings together the Nao outputs, the
        speech recognition, the chess games, the recording of the participant data, etc...


        Parameters
        ----------
        interaction_settings : experimentNao.interaction.interaction_settings.InteractionSettings
            the settings of the interaction (if nao is connected, if we are with the participant, the mode of
            interaction, etc...)
        id_conf : experimentNao.model_ID.configs.overall_config.IDConfig
            configuration of the theory of mind model
        """
        # Set relevant data:
        self.n_puzzles_per_group = 3
        self.max_number_of_puzzles = 30 if not interaction_settings.demo else 1
        self.max_time_of_interaction = 60*60 if interaction_settings.interaction_mode == InteractionMode.TRAINING else 35*60
        self.model_config = id_conf.model_config
        # Initialize relevant data:
        self.writer = None
        self.counter = Counter(0, 0)    # to keep track of puzzle number & periodic hints
        self.skipped_puzzle, self.quit = False, False
        self.interaction_settings = interaction_settings
        self.interaction_mode = interaction_settings.interaction_mode
        self.participant_id = id_conf.participant_id
        self.random, self.seed = None, None
        self.interaction_starting_time = time.time()
        self.init_random()
        # Interaction mode
        if self.interaction_mode == InteractionMode.TRAINING:
            self.controller = pc.PredefinedController(self.max_number_of_puzzles, self.n_puzzles_per_group,
                                                      session=interaction_settings.session_number)
            self.tom_model = dem.get_model_from_config(id_conf, dem.get_normalization_values_of_rld(None))
        else:
            if self.interaction_mode == InteractionMode.MBC:
                self.controller = mbc.ModelBasedController(id_conf, verbose=2)
            elif self.interaction_mode == InteractionMode.ALTERNATIVE_C:
                self.controller = ac.AlternativeController(id_conf, self.max_time_of_interaction, verbose=1)
            self.tom_model = self.controller.tom_model
        # Systems of the interaction
        self.nao_client = nao_requests.NaoClient() if interaction_settings.with_nao else None
        self.speech_recognizer = sr.SpeechRecognizer()
        self.participant_requests = participant_requests.RequestsHolder(self)
        self.conversation_manager = convo.ConversationManager(self.nao_client, self.speech_recognizer, self)
        self.chess_engine = my_chess_engine.MyChessEngine(interaction_mode=True, lichess_db=interaction_settings.lichess_db,
                                                          interaction_number=self.interaction_settings.session_number)
        self.chess_display = g_sim.GraphicSimulation(self.chess_engine, self.participant_requests, interaction_mode=True,
                                                     second_screen=interaction_settings.second_screen)
        self.set_connection_between_chess_engine_and_gui()
        self.performance_indicators = pi.PerformanceIndicators()
        self.feedback_manager = parti_fb.ParticipantFeedback(self, self.interaction_mode == InteractionMode.TRAINING)
        self.helping_system = hints.HelpingSystem(self.chess_engine, nao_helping=False, random_=self.random)
        self.reward_system = rs.RewardSystemScheduled(self.nao_client, self.conversation_manager.output_command,
                                                      self.random, self.n_puzzles_per_group, self.max_number_of_puzzles)
        if self.interaction_mode == InteractionMode.MBC or self.interaction_mode == InteractionMode.ALTERNATIVE_C:
            self.initialize_session_with_controller()
        self.run_interaction()

    def run_interaction(self):
        """ runs the interaction that was designed to id the model for participants

        """
        if self.interaction_settings.demo or self.interaction_mode == InteractionMode.MBC or InteractionMode.ALTERNATIVE_C:
            if self.interaction_settings.say_hello:
                self.conversation_manager.interaction_introduction()         # introduction and ask for name
        self.writer = self.create_excel()  # create excel
        self.play_puzzles()
        self.feedback_manager.writer.close()
        if self.interaction_settings.demo:
            self.conversation_manager.output_command('You finish the demo. Time to play!')
        else:
            self.conversation_manager.output_command('We finished this session! It was nice playing with you.')
        self.chess_display.main_window.close_window()

    def play_puzzles(self):
        """ manages the puzzles that are shown to the participants. Starts by explaining instructions, enables the mic
        to listen in the background, selects the next puzzle and runs it. The next characteristics of the next puzzle
        are defined in 'set_next_puzzle'.

        Returns
        -------
        None
        """
        if self.interaction_settings.demo or self.interaction_settings.speak_instructions:
            self.conversation_manager.give_instructions()
        self.conversation_manager.state_starting_puzzles()
        self.conversation_manager.listen_for_request_in_background()
        self.feedback_manager.reset_periodic_action()
        while self.interaction_not_done():
            self.pre_process_before_puzzle()
            self.run_a_puzzle()
            self.post_process_of_puzzle()
            if self.quit:
                return
            self.chess_display.main_window.clear_window()
            self.counter.current_puzzle += 1

    def run_a_puzzle(self):
        """ runs a puzzle for the right amount of moves.

        """
        while self.chess_engine.current_move_in_puzzle < self.chess_engine.current_puzzle.number_of_moves:
            computer_turn = not self.chess_engine.is_humans_turn()
            self.chess_engine.manage_next_move()
            if computer_turn:
                self.conversation_manager.say_move_out_loud(self.chess_engine.opponent_next_move)
            if self.quit or self.skipped_puzzle:
                break

    def pre_process_before_puzzle(self):
        """ runs the required functions to prepare for the next puzzle (before the next puzzle is actually run)

        """
        if self.counter.current_puzzle != 0:
            self.conversation_manager.introduce_another_puzzle()
        if self.interaction_mode == InteractionMode.TRAINING:
            if self.counter.current_puzzle == self.controller.recommended_number_of_puzzles:
                self.conversation_manager.recommended_amount_of_puzzles_reached(self.controller.recommended_number_of_puzzles)
            self.chess_engine.current_difficulty, self.helping_system.nao_helping, self.reward_system.nao_offering_rewards \
                = self.controller.get_characteristics_of_puzzle(self.counter.current_puzzle)
        elif self.interaction_mode == InteractionMode.MBC or self.interaction_mode == InteractionMode.ALTERNATIVE_C:
            self.chess_engine.current_difficulty = self.controller.get_puzzle_difficulty_status()
        self.feedback_manager.reset_beginning_of_puzzle()
        self.chess_display.set_counter(self.counter.current_puzzle)
        self.helping_system.new_puzzle_resets()
        self.performance_indicators.reset_performance_indicators()
        self.skipped_puzzle = False
        self.set_new_puzzle()
        self.controller.reset_beginning_of_puzzle(self.chess_engine.current_puzzle.number_of_moves)

    def post_process_of_puzzle(self):
        """ runs the functions that are necessary to be run after a puzzle is completed

        """
        skip_or_quit = self.skipped_puzzle or self.quit
        self.performance_indicators.save_indicators(self.chess_engine, self.helping_system, self.reward_system,
                                                    self.skipped_puzzle)
        if self.interaction_mode == InteractionMode.MBC or self.interaction_mode == InteractionMode.ALTERNATIVE_C:
            if self.skipped_puzzle and self.counter.current_puzzle == 0:    # if participant requests skip in 1st puzzle
                print('Skipped on first puzzles: special case')
                self.run_discrete_time_step_task()
            self.controller.update_end_of_puzzle_and_get_action(self.performance_indicators.indicators, self.counter.current_puzzle)
            self.reward_system.nao_offering_rewards = self.controller.get_give_reward_status()
        self.conversation_manager.comment_on_end_of_puzzle(skip_or_quit, self.reward_system.nao_offering_rewards)
        if self.interaction_mode == InteractionMode.MBC or self.interaction_mode == InteractionMode.ALTERNATIVE_C:
            given = self.reward_system.give_random_reward()
            self.performance_indicators.indicators.reward_given = given
        elif self.interaction_mode == InteractionMode.TRAINING:
            self.reward_system.update_and_run(skip_or_quit, self.counter.current_puzzle)
            self.performance_indicators.indicators.reward_given = self.reward_system.reward_given_in_puzzle[-1]
        self.print_indicators()
        self.performance_indicators.write_indicators_2_excel(self.counter.current_puzzle, self.quit)
        self.ask_for_feedback(parti_fb.FBEvent.QUIT if self.quit else parti_fb.FBEvent.END_PUZZLE)
        if self.quit:
            self.conversation_manager.output_command('I am sorry to see you go.')

    def set_new_puzzle(self):
        """ selects and sets a new puzzle while making sure it has the suitable length

        """
        success = False
        while not success:
            self.chess_engine.set_new_puzzle()
            puzzle = self.chess_engine.current_puzzle
            success = self.controller.reset_beginning_of_puzzle(puzzle.number_of_moves)
        self.performance_indicators.save_puzzle_info(puzzle)    # write to excel the info of the puzzle
        if verbose.VERBOSE.basic_info:
            print('We are playing puzzle ' + (puzzle.url if puzzle.url is not None else str(puzzle.tag)) + ' , difficulty ' + str(puzzle.difficulty))

    def show_board_and_ask_for_move(self, current_move, last_move):
        """

        Parameters
        ----------
        current_move : int
            number of the current move (1st move of puzzle is 0)
        last_move : bool
            whether this is the last move
        """
        self.helping_system.new_move_resets()
        # 1. set up board
        if current_move == 0:  # if it is the first move - start simulation
            self.chess_display.start_simulation(last_move)
        else:  # if not, just resume it
            self.conversation_manager.ask_for_another_move()
            self.chess_display.resume_simulation(last_move)
        # 2. run the window loop of interaction with participant
        while not self.chess_engine.move_chosen:    # Loop of graphical
            if self.feedback_manager.ask_asynchronous_feedback:     # ask time's up
                self.run_discrete_time_step_task()
            self.handle_mic_reset()
            self.chess_display.run_simulation_interaction_mode()
            if self.check_and_handle_participants_requests():
                return
        # 3. Move made and received.
        self.performance_indicators.save_number_wrong_moves_in_turn(self.chess_engine)
        if last_move:  # Is it last move of puzzle? if so, finish simulation
            self.chess_display.finish_puzzle_simulation()
            self.skipped_puzzle = False
        else:
            self.conversation_manager.celebrate_right_move()
            if self.controller.check_if_it_is_discrete_time_step(current_move):   # ask in middle of puzzle
                self.run_discrete_time_step_task()  # either ask for feedback or run model

    def run_discrete_time_step_task(self):
        """ run the tasks that must be taken every discrete time step of the controller

        """
        self.save_and_write_indicators()
        self.ask_for_feedback(parti_fb.FBEvent.MID_PUZZLE)
        if self.interaction_mode == InteractionMode.MBC or self.interaction_mode == InteractionMode.ALTERNATIVE_C:
            self.controller.update_model_middle_of_question(self.performance_indicators.indicators,
                                                            self.feedback_manager.time_step_answers,
                                                            self.counter.current_puzzle)
            self.feedback_manager.reset_periodic_action()

    def ask_for_feedback(self, feedback_circumstance):
        """ asks the participant for feedback.

        """
        if self.controller.ask_questions(self.counter.current_puzzle,
                                         mid_puzzle=(feedback_circumstance == parti_fb.FBEvent.MID_PUZZLE)):
            st = time.time()    # write down the time spent in question (to subtract at the end)
            self.conversation_manager.ask_for_feedback()
            if self.interaction_settings.ask_for_feedback:
                self.feedback_manager.ask_feedback_from_participant(feedback_circumstance)
            else:
                if verbose.VERBOSE.basic_info:
                    print(' [Info] Wont ask questions in debug mode')
                    self.feedback_manager.reset_periodic_action()
            self.performance_indicators.times_spent_in_questions.append(time.time() - st)

    def ask_for_feedback_before_question(self, n_times_question_asked_before_helping):
        """

        Parameters
        ----------
        n_times_question_asked_before_helping : int
            number of times that the questions before helping were asked in the current puzzle
        """
        if self.interaction_mode == InteractionMode.TRAINING:
            self.conversation_manager.ask_for_feedback()
            self.feedback_manager.ask_feedback_before_helping_participant(n_times_question_asked_before_helping)

    def check_and_handle_participants_requests(self):
        """ checks and handles the requests of the participants to get help, skip, or quit

        Returns: bool
            Whether the puzzle should be interrupted
        -------

        """
        self.conversation_manager.check_participant_requests(self.performance_indicators.indicators)
        for request in self.participant_requests.get_requests():
            if request.participant_wants_it:
                request.request_function()
                request.participant_wants_it = False
                return request.interrupt_puzzles_when_activated
        return False

    def handle_mic_reset(self):
        """ handles the mic reset

        """
        if self.chess_display.microphone_needs_reset:
            self.conversation_manager.reset_listen_for_request_in_background()
            self.chess_display.microphone_needs_reset = False

    def set_connection_between_chess_engine_and_gui(self):
        """ sets the functions that connect the chess engine requests (asking for a move and displaying a move made by
        the engine) with the graphical user interface. These functions are methods of this class, in order to manage
        the connection

        """
        self.chess_engine.set_graphic_simulation(self.chess_display)
        self.chess_engine.set_function_that_shows_board_and_asks_for_move(lambda current_move, last_move:
                                                                          self.show_board_and_ask_for_move(current_move,
                                                                                                           last_move))
        self.chess_engine.set_function_that_displays_computers_move(lambda best_move: self.play_engine_move(best_move))

    def skip_puzzle(self):
        """ manages action "skip puzzle"

        """
        self.skipped_puzzle = True
        print('skipped')

    def give_help(self):
        """ manages action "get help"

        """
        self.helping_system.help_participant(self, self.conversation_manager)
        print('help given')

    def set_quit_flag(self):
        """ manages action "quit" by setting up the flag that the participant asked to quit, which is then enforced

        """
        self.quit = True
        print('quit')

    def play_engine_move(self, engine_move):
        """

        Parameters
        ----------
        engine_move : str
            the chess move that the computer(chess engine) will play
        """
        self.chess_display.run_computer_move(engine_move)

    def interaction_not_done(self):
        """ whether the interaction is done after the current puzzle or not

        Returns
        -------
        bool
        """
        if self.interaction_mode == InteractionMode.TRAINING:
            return self.counter.current_puzzle < self.max_number_of_puzzles
        else:
            return time.time() - self.interaction_starting_time < self.max_time_of_interaction

    def give_periodic_hint(self):
        """ gives a hint every X interaction

        """
        self.counter.periodic_hints_counter += 1
        if self.counter.periodic_hints_counter == 200000:
            self.counter.periodic_hints_counter = 0
            self.conversation_manager.help_participant()

    def save_and_write_indicators(self):
        """ save and write the interaction indicators to the Excel file

        """
        self.performance_indicators.save_and_write_indicators(self.chess_engine, self.counter.current_puzzle,
                                                              self.helping_system, self.reward_system,
                                                              self.skipped_puzzle, self.quit)

    def initialize_session_with_controller(self):
        """
        Initialize the variables needed in the third session, when the controller of the robot is in used

        """
        self.helping_system.nao_helping = True
        self.reward_system.nao_offering_rewards = False
        next_difficulty = 3
        self.controller.initialize_controller(next_difficulty, self.helping_system.nao_helping,
                                              self.reward_system.nao_offering_rewards)
        self.chess_engine.current_difficulty = self.controller.next_puzzle_difficulty

    def print_indicators(self):
        """ print the indicators of the interaction to the console

        """
        if verbose.VERBOSE.basic_info:
            print(' [Info] Time to solve: ', self.performance_indicators.indicators.time_2_solve,
                  '\t Wrong attempts: ', self.performance_indicators.indicators.n_wrong_attempts)

    def create_excel(self):
        """ creates excel and adds it to the relevant modules

        Returns
        -------
        pandas.io.excel._openpyxl.OpenpyxlWriter
        """
        name = ''
        path = folder_path.output_folder_path / 'replies_participants'
        if self.interaction_mode == InteractionMode.MBC:
            name = 'Output'
            path = path / 'mbc_session'
        elif self.interaction_mode == InteractionMode.TRAINING:
            name = 'Reply'
            path = path / 'training_sessions'
        elif self.interaction_mode == InteractionMode.ALTERNATIVE_C:
            name = 'Output_alternative'
            path = path / 'mbc_session'
        if self.interaction_settings.save_excel:
            name += '_{}_{}.xlsx'.format(self.participant_id, time.time())
        else:
            name += '.xlsx'
        writer = excel_files.create_excel_file(str(path / name))
        self.performance_indicators.set_excel(writer)
        self.feedback_manager.set_excel(writer)
        if self.interaction_mode == InteractionMode.MBC or self.interaction_mode == InteractionMode.ALTERNATIVE_C:
            self.controller.controller_writer.set_excel(writer)
        return writer

    def init_random(self):
        """ initialize the random variable

        """
        if self.seed is None:
            self.seed = random.randrange(sys.maxsize)
        self.random = random.Random(self.seed)


class Counter:
    def __init__(self, puzzle_counter, periodic_hints_counter):
        """ Initialize the counters needed for the interaction

        Parameters
        ----------
        puzzle_counter : int
        periodic_hints_counter : int
        """
        self.current_puzzle = puzzle_counter
        self.periodic_hints_counter = periodic_hints_counter


class InteractionMode(Enum):    # Interaction modes
    TRAINING = 1
    MBC = 2
    ALTERNATIVE_C = 3
