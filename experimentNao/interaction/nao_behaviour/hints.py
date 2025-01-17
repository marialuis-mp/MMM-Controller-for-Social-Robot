from enum import Enum

from experimentNao.interaction import verbose


class HintTypes(Enum):
    TYPE_OF_MOVE = 1
    TYPE_OF_PIECE_TO_MOVE = 2
    SAY_MOVE = 3


class HelpingSystem:
    def __init__(self, chess_engine, nao_helping, random_):
        """ system that coordinates the hints given by Nao to the participants

        Parameters
        ----------
        chess_engine : experimentNao.chess_game.my_chess_engine.MyChessEngine
            the chess engine that handles the puzzles and defines the next moves
        nao_helping : bool
            whether Nao is helping or hindering (i.e., giving wrong hints on purpose)
        random_ : random.Random
            the random variable, to ensure traceability
        """
        self.chess_engine = chess_engine
        self.nao_helping = nao_helping
        self.pause = ' \\pau=150\\ '
        self.random = random_
        # Flags
        self.hint_puzzle_type_given = False
        self.hint_piece_type_given = False
        # Hints data
        self.probability_of_asking_question_before_helping = 0.8
        self.n_times_fb_asked_when_help_requested_per_puzzle = 0   # n of times the participant was asked for feedback
        self.max_times_fb_asked_when_help_requested_per_puzzle = 1
        self.n_times_fb_asked_when_help_requested_ttl = 0
        self.max_times_fb_asked_when_help_requested_ttl = 6
        self.slow_speech_speed = 90
        self.normal_speech_speed = 110

    # ************************* Resets *************************
    def new_puzzle_resets(self):
        """ resets flag variables and counters when a new puzzle starts

        """
        self.hint_puzzle_type_given = False
        self.hint_piece_type_given = False
        self.n_times_fb_asked_when_help_requested_per_puzzle = 0

    def new_move_resets(self):
        """ resets flag variables and counters when a new move is awaited

        """
        self.hint_piece_type_given = False

    def help_participant(self, interaction, conversation_manager):
        """ Gives the hint to the participants

        Parameters
        ----------
        interaction : experimentNao.interaction.interaction_manager.Interaction
        conversation_manager : experimentNao.interaction.nao_behaviour.conversation_manager.ConversationManager
        """
        conversation_manager.speech_recognizer.stop_listening_in_background()
        conversation_manager.inform_of_help()
        self.check_asking_questions_b4_helping(interaction)
        hint_type = self.select_type_of_hint()
        hint = self.generate_hint(hint_type)
        change_speed_of_speech(interaction.nao_client, self.slow_speech_speed)  # show down
        conversation_manager.output_command(hint)
        change_speed_of_speech(interaction.nao_client, self.normal_speech_speed)  # Fast again
        interaction.performance_indicators.hint_given()
        if hint_type == HintTypes.SAY_MOVE:
            interaction.performance_indicators.move_revealed()
        conversation_manager.listen_for_request_in_background()

    def check_asking_questions_b4_helping(self, interaction):
        """ checks whether the current help request requires asking questions to the participants beforehand

        Parameters
        ----------
        interaction : experimentNao.interaction.interaction_manager.Interaction
        """
        if self.random.random() < self.probability_of_asking_question_before_helping and \
                self.n_times_fb_asked_when_help_requested_ttl < self.max_times_fb_asked_when_help_requested_ttl and \
                self.n_times_fb_asked_when_help_requested_per_puzzle < self.max_times_fb_asked_when_help_requested_per_puzzle:
            if verbose.VERBOSE.helping_information:
                print(' [H] Asking questions before help')
            interaction.ask_for_feedback_before_question(self.n_times_fb_asked_when_help_requested_per_puzzle)
            self.n_times_fb_asked_when_help_requested_per_puzzle += 1
            self.n_times_fb_asked_when_help_requested_ttl += 1

    def generate_hint(self, hint_type):
        """ generates the text with the hint to be given

        Parameters
        ----------
        hint_type : experimentNao.interaction.nao_behaviour.hints.HintTypes
            type of the hint (depending on the number of the move)

        Returns
        -------
        str
        """
        hint = None
        if hint_type == HintTypes.SAY_MOVE:
            move = self.chess_engine.ideal_move
            hint = 'The right move is' + self.pause + move[0:2] + self.pause + move[2:4]
        elif hint_type == HintTypes.TYPE_OF_PIECE_TO_MOVE:
            starting_pos_ideal_move = self.chess_engine.get_positions_of_ideal_move()[0]
            if self.nao_helping:
                piece, name = self.chess_engine.piece_in_position(starting_pos_ideal_move)
            else:
                wrong_starting_pos = next((str(move)[0:2] for move in self.chess_engine.board.legal_moves
                                           if starting_pos_ideal_move not in str(move)), starting_pos_ideal_move)
                piece, name = self.chess_engine.piece_in_position(wrong_starting_pos)
            hint = self.give_type_to_move_hint(name)
        elif hint_type == HintTypes.TYPE_OF_MOVE:
            correct_type = self.chess_engine.current_puzzle.type.lower()
            # correct_type = correct_type.split(' ')[0]
            if self.nao_helping:
                hint = self.give_type_of_puzzle_hint(correct_type)
            else:
                wrong_type = 'check' if 'check' not in correct_type else 'fork' if 'fork' not in correct_type else 'capture'
                hint = self.give_type_of_puzzle_hint(wrong_type)
        return hint

    def give_type_to_move_hint(self, name_of_piece_2_move):
        """ generates the text for hints of type TYPE_OF_PIECE_TO_MOVE

        Parameters
        ----------
        name_of_piece_2_move : str
            name of piece to move

        Returns
        -------

        """
        hint = self.random.choice(['Have you took a look at your' + self.pause + name_of_piece_2_move + '?',
                                   'Maybe you can move your' + self.pause + name_of_piece_2_move + '.'])
        return hint

    def give_type_of_puzzle_hint(self, puzzle_type: str):
        """ generates the text for hints of type TYPE_OF_MOVE

        Parameters
        ----------
        puzzle_type : str
            type of the piece that should be moved

        Returns
        -------
        str
        """
        if 'mate' in puzzle_type:       # check , check-mate
            hint = 'Can you give a ' + self.pause + 'check-mate?'
        elif 'check' in puzzle_type:       # check , check-mate
            hint = 'Can you give a ' + self.pause + 'check?'
        elif 'fork' in puzzle_type:
            hint = 'Is there any ' + self.pause + 'fork that you can think of?'
        elif 'sacrifice' in puzzle_type:
            hint = 'Is there any sacrifice that you can think of?'
        elif 'capture' in puzzle_type:
            hint = 'You can capture a piece. Can you find out how?'
        elif 'pin' in puzzle_type:
            hint = 'Can you pin any piece?'
        elif 'advanced pawn' in puzzle_type:
            hint = 'Can you protect the advanced pawn?'
        elif 'endgame' in puzzle_type:
            hint = 'This is an endgame type of puzzle!'
        elif 'advantage' in puzzle_type:
            hint = 'Is there any way for you to gain an advantage in this puzzle?'
        elif 'defense' in puzzle_type:
            hint = 'Maybe you should focus on defense.'
        else:
            hint = 'This puzzle is about performing a ' + self.pause + puzzle_type.split(' ')[0]
        return hint

    def select_type_of_hint(self):
        """ figures out which type of hint should be given currently, depending on the current values of the flags

        Returns
        -------
        experimentNao.interaction.nao_behaviour.hints.HintTypes
        """
        if not self.hint_puzzle_type_given:
            hint_type = HintTypes.TYPE_OF_MOVE
            self.hint_puzzle_type_given = True
        elif not self.hint_piece_type_given:
            hint_type = HintTypes.TYPE_OF_PIECE_TO_MOVE
            self.hint_piece_type_given = True
        else:
            hint_type = HintTypes.SAY_MOVE
        return hint_type


def change_speed_of_speech(nao_client, new_speed):
    """ changes the speed of the speech

    Parameters
    ----------
    nao_client : Union[nao_requests.NaoClient, None]
    new_speed : int
    """
    if nao_client is not None:
        nao_client.change_speed_of_speech(new_speed)
