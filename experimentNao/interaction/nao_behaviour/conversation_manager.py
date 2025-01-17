from threading import Lock
import pyttsx3
from experimentNao.interaction import verbose
from experimentNao.interaction.nao_behaviour.requests_enums import BodyMovements
import re


class ConversationManager:
    def __init__(self, nao_client, speech_recognizer, interaction):
        """ manages the speech generation of the robot (or the computer, if the robot is not connected), and the output
        of the generated speech, either through the robot or teh computer.

        Parameters
        ----------
        nao_client : Union[experimentNao.interaction.nao_behaviour.nao_requests.NaoClient, None]
        speech_recognizer : lib.speech_recognition_module.my_speech_recognition.SpeechRecognizer
        interaction : experimentNao.interaction.interaction_manager.Interaction
        """
        self.output_command = (lambda text: nao_client.make_nao_say_something(text)) \
            if interaction.interaction_settings.with_nao else (lambda text: self.speak_without_nao(text))
        self.speech_recognizer = speech_recognizer
        self.interaction = interaction
        self.participant_requests = interaction.participant_requests
        # Participant info
        if not interaction.interaction_settings.with_nao:                                   # when they asked for help
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 250)
        self.random = interaction.random
        self.confirmation_mode = False   # for callback
        self.request_in_confirmation = False
        if not interaction.interaction_settings.with_nao:
            self.mutex = Lock()

    # ************************* Interactions and specific dialogues *************************
    def interaction_introduction(self, ask_for_name=False):
        """ runs the introduction of the interaction, with Nao introducing the interaction purpose, himself, and asking
        the participant for their name.

        Parameters
        ----------
        ask_for_name : whether Nao should ask for the name of the participant during the interaction

        """
        self.make_body_movement(BodyMovements.HELLO, async_=True)
        self.output_command('Hello! \\pau=700\\ Today we will be playing some chess puzzles. \\pau=200\\')
        if ask_for_name:
            self.make_body_movement(BodyMovements.YOU, async_=True)
            self.ask_for_name()
            self.output_command('\\pau=100\\ Nice to meet you! ')
        self.make_body_movement(BodyMovements.ME, async_=True)
        self.output_command('\\pau=100\\ I am Nao.')
        if not ask_for_name:
            self.output_command('\\pau=300\\ Nice to meet you! ')

    def give_instructions(self):
        """ outputs the instructions of the puzzle to the participant, using the selected output channel

        """
        self.output_command('\\pau=1000\\ I will explain some instructions now')
        self.make_body_movement(BodyMovements.EXPLAIN, async_=True)
        self.output_command('\\pau=1000\\ The puzzle will show up on the screen. \\pau=500\\ '
                            'You can choose and play the best move \\pau=100\\ with the mouse. \\pau=500\\ ')
        self.make_body_movement(BodyMovements.YOU, async_=True)
        self.output_command('To do so, click on the piece you want to move, and click again in the position where '
                            'you want to move it to. ')
        self.output_command('\\pau=1000\\ If you cannot guess the best move,')
        self.make_body_movement(BodyMovements.ME, async_=True)
        self.output_command('and you need help, just ask me for help \\pau=500\\ or for a hint.')
        self.output_command('\\pau=200\\ If you are stuck on a puzzle for a while, you can ask me to skip it.')
        self.output_command('\\pau=200\\ You can ask to quit at any time.')
        self.output_command('\\pau=500\\ On the right top corner, there is a counter with the amount of puzzles '
                            'that you have played.')

    def state_starting_puzzles(self):
        """ Introduce start of puzzles

        """
        self.make_body_movement(BodyMovements.YOU_KNOW_WHAT, async_=True)
        self.output_command("\\pau=1200\\ Let's start with the puzzles!")

    def ask_for_name(self):
        """ ask for participant's name

        Returns
        -------

        """
        self.output_command('\\pau=200\\ What is your name?')
        recognized_text = self.speech_recognizer.listen_and_recognize_sentence(output_source=self.output_command,
                                                                               time_limit=5)
        if recognized_text is None:
            return
        else:
            for additive in ['name is ', 'I am ', "I'm "]:
                if additive in recognized_text:     # if recognized text contains one of the following:
                    index = recognized_text.find(additive) + len(additive)
                    name = recognized_text[index:]
                    break                           # if it doesn't, we assume entire text is the name
                name = recognized_text
        self.output_command('Is your name ' + name + '?')
        recognized_reply = self.speech_recognizer.listen_and_recognize_sentence(output_source=self.output_command,
                                                                                time_limit=5)
        if recognized_reply != 'yes':
            self.ask_for_name()
        else:
            self.interaction.participant_id = name

    def comment_on_end_of_puzzle(self, quit_or_skipped, nao_offering_rewards):
        """ speech for the end of puzzle

        Parameters
        ----------
        quit_or_skipped : whether the current puzzle as skipped or the participant quit
        nao_offering_rewards : if Nao is currently offering reward
        """
        if quit_or_skipped:
            self.console_after_skipping_puzzle()
        else:
            self.celebrate_end_of_puzzle(nao_offering_rewards)

    def ask_for_another_move(self):
        """ speech to ask for another move

        """
        if self.random.random() < 0.2:
            self.make_body_movement(BodyMovements.YOU, async_=True)
        self.output_command(self.random.choice(["Find the next move of this puzzle!", "Find the next move!",
                                                "Guess the next move of this puzzle!", "Guess the next move!",
                                                "Can you find the next move? ",
                                                "Try to find the next move.",
                                                "Can you guess the next move.",
                                                "Will you guess the next move?"]))

    def celebrate_right_move(self):
        """ speech that celebrates when the participant guessed the move correctly

        """
        pre_string = self.random.choice(['You found the right move! ', 'You guessed the move! ', 'You guessed it! ',
                                         'That was the right move, ', 'That was the correct move, ',
                                         'Correct, ', 'Precisely, ', 'Perfect, '])
        post_string_empty = self.random.choice([False, True, True])
        if post_string_empty:
            pos_string = ''
        else:
            pos_string = self.random.choice(['but the puzzle is not over!', 'but the puzzle is not over yet!',
                                             'Keep going', "but it's not over!"])
        self.output_command(pre_string + pos_string)

    def celebrate_end_of_puzzle(self, nao_offering_rewards):
        """ speech that celebrates when the participant finishes a puzzle

        """
        self.make_body_movement(BodyMovements.EXCITED, async_=True)
        pre_string = self.random.choice(['Very well! ', 'Good job! ', 'Nice! ', '']) if nao_offering_rewards else ''
        type_of_celebration = self.random.choice(['S', 'E'])
        puzzle_pronoun = self.random.choice(['this puzzle', 'this one', 'the puzzle'])
        txt = ''
        if type_of_celebration == 'S':
            txt = self.random.choice(['You solved', 'You finished', 'You completed']) + ' ' + puzzle_pronoun
        elif type_of_celebration == 'E':
            txt = puzzle_pronoun + ' ' + self.random.choice([' is done!', 'is finished'])
        self.output_command(pre_string + txt)

    def console_after_skipping_puzzle(self):
        """ speech that consoles participant after skipping the puzzle

        """
        self.output_command(self.random.choice(["You will do better next time!",
                                                "This one was tough!"]))

    def introduce_another_puzzle(self):
        """ speech that introduces a new puzzle

        """
        self.make_body_movement(BodyMovements.YES, async_=True)
        txt_start = self.random.choice(["Let's try", "I'll give you", "Let's play"])
        txt_end = self.random.choice(["another puzzle", "another one", "more puzzles"])
        self.output_command("\\pau=100\\" + txt_start + ' ' + txt_end)

    def inform_of_help(self):
        """ speech that introduces help

        """
        txt_start = self.random.choice(["I'll ", "I'm going to "])
        txt_end = self.random.choice(["help you.", "give you a hint"])
        self.output_command(txt_start + ' ' + txt_end + '\\pau=1000\\')

    def ask_for_feedback(self, before_helping=False):
        """ speech that introduces the questions asked the participants about their mental states

        Parameters
        ----------
        before_helping : bool
            if the questions are being asked before a help request

        """
        pre_string = 'But first, ' if before_helping else '\\pau=1000\\ '
        pos_string = '\\pau=1000\\ ' if before_helping else ''
        start_txt = self.random.choice(['Can you', 'Could you', 'Would you'])
        middle_txt = self.random.choice(['answer', 'please answer', 'reply to', 'please reply to'])
        end_txt = self.random.choice(['the following questions?', 'these questions?', 'these questions?'])
        self.output_command(pre_string + start_txt + ' ' + middle_txt + ' ' + end_txt + pos_string)

    def recommended_amount_of_puzzles_reached(self, recommended_number_of_puzzles):
        """ speech that informs the participants that they played the right ammount

        Parameters
        ----------
        recommended_number_of_puzzles : int
            the number of puzzles that is the minimum recommended

        """
        pre_text = self.random.choice(['I want to let you know that ', 'For your information, '])
        text = 'you have played {} puzzles, the minimum recommended amount'.format(recommended_number_of_puzzles)
        self.output_command(pre_text + text)

    def say_move_out_loud(self, opponent_next_move):
        """ speech that states the chess move taken by the robot

        Parameters
        ----------
        opponent_next_move : str
            the next chess move of the robot

        """
        pre_text = self.random.choice(['', '', '', 'I move', 'I play'])
        piece_moved = self.interaction.chess_engine.piece_in_position(opponent_next_move[2:4])
        self.output_command(pre_text + ' ' + piece_moved[1] + ' to ' + opponent_next_move[2:4])

    def ask_participant_to_repeat_request(self):
        """ speech that asks the participant to repeat their request

        """
        pre_txt = self.random.choice(['I did not understand.', 'I am afraid I did not understand.'])
        post_txt = self.random.choice(['Make your request again, please.', 'Please repeat your request.'])
        self.output_command(pre_txt + ' ' + post_txt)

    # ************************* Microphone *************************
    def listen_for_request_in_background(self):
        """ activates the listening in the background function of the microphone, setting the method
        self.process_participant_voice_request as callback.

        """
        self.speech_recognizer.listen_in_background(self.process_participant_voice_request, False,
                                                    phrase_time_limit=3)
        if verbose.VERBOSE.microphone_information:
            print(' [M] Started listening in background')

    def reset_listen_for_request_in_background(self):
        """ resets the function of the microphone to listen in the background

        """
        self.speech_recognizer.stop_listening_in_background()
        self.listen_for_request_in_background()

    # ************************* Reply to requests *************************
    def process_participant_voice_request(self, recognizer, audio):
        """ processes the request made by the participant through the microphone. This function should be given as the
        callback of the speech recognition package

        Parameters
        ----------
        recognizer : speech_recognition.Recognizer
            required by the structure that is imposed in the callback of the speech recognition package
        audio : speech_recognition.audio.AudioData
            audio data that was captured by the microphone
        """
        if not self.confirmation_mode:
            for request in self.participant_requests.get_requests():
                if request.process_voice_request(self.speech_recognizer, audio):
                    break
        else:
            if self.speech_recognizer.look_for_words_in_audio(words_2_look_4=['yes', 'I do', 'sure'], audio=audio):
                self.request_in_confirmation.participant_wants_it = True
            elif self.speech_recognizer.look_for_words_in_audio(words_2_look_4=['no'], audio=audio):
                self.request_in_confirmation.participant_wants_it = False
                self.output_command('I am sorry, I misunderstood you.')
            else:
                self.ask_participant_to_repeat_request()
            print(' [M] Confirmation ended. Participant wanted help: ', self.request_in_confirmation.participant_wants_it)
            self.confirmation_mode = False
            self.request_in_confirmation = None

    def check_participant_requests(self, indicators):
        """ goes through potential requests of participants and selects the one that was requested, if any

        Parameters
        ----------
        indicators : experimentNao.declare_model.chess_interaction_data.ChessInteractionData
            interaction indicators
        """
        for request in self.participant_requests.get_requests():
            if request.participant_might_want_it:
                self.request_in_confirmation = request
                question = self.participant_requests.get_question(request, indicators.n_hints)
                self.confirm_participant_request(question)
                break   # if one request was attended, do not accept more requests

    def confirm_participant_request(self, question):
        """ speech to confirm the request that is thought to be asked by the participant (and deactivation of the flags
        that triggered this confirmation)

        Parameters
        ----------
        question : str
            question to be asked to the participant
        """
        self.output_command(question)
        self.confirmation_mode = True
        self.request_in_confirmation.participant_might_want_it = False   # either it was misunderstood or request will be filled

    def check_if_participant_accepted(self):
        """ get answer to confirmation of request

        Returns
        -------

        """
        recognized_text = self.speech_recognizer.listen_and_recognize_sentence(number_attempts=2, time_limit=3)
        if isinstance(recognized_text, str):
            if 'yes' in recognized_text.lower() or 'i do' in recognized_text.lower():
                return True
        return False

    def make_body_movement(self, body_movement, async_=True):
        """ make body movement (to be used with txt output)

        Parameters
        ----------
        body_movement : experimentNao.interaction.nao_behaviour.requests_enums.BodyMovements
        async_ : bool
        """
        if self.interaction.nao_client is not None:
            self.interaction.nao_client.make_body_movement(body_movement, async_=async_)

    def speak_without_nao(self, text):
        """ function that handles the output of the speech when Nao is not connected

        Parameters
        ----------
        text : str
            string of text to be spoken by Nao
        """
        with self.mutex:
            text = re.sub(r'\\pau=\d+\\', '', text)
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()


