from enum import Enum

from experimentNao.interaction import verbose


class RequestsHolder:
    def __init__(self, interaction):
        """ object that manages the requests that the participant can ask

        Parameters
        ----------
        interaction : experimentNao.interaction.interaction_manager.Interaction
        """
        self.request_graphic_check_in_progress = False
        self.skip_request = Request(('skip', 'move on'), txt_button='Skip puzzle',
                                    question='Do you want to skip this puzzle?',
                                    request_function=interaction.skip_puzzle, interrupt_puzzles_when_activated=True)
        self.quit_request = Request(('quit',), txt_button='Quit interaction',
                                    question='Do you want to quit the game? Once you quit, you cannot restart it.',
                                    request_function=interaction.set_quit_flag, interrupt_puzzles_when_activated=True)
        self.help_request = Request(('help', 'hint'), txt_button='Get help',
                                    question='Do you want a hint?', question_alternative='Do you want another hint?',
                                    request_function=interaction.give_help, interrupt_puzzles_when_activated=False)

    def get_requests(self):
        """ gets the list of all the requests

        Returns
        -------
        Tuple[experimentNao.interaction.nao_behaviour.participant_requests.Request]
        """
        return self.help_request, self.skip_request, self.quit_request

    def get_question(self, request, n_hints):
        """ gets the question text to ask the participant to confirm their request

        Parameters
        ----------
        request : experimentNao.interaction.nao_behaviour.participant_requests.Request
        n_hints : int

        Returns
        -------

        """
        if request == self.help_request:
            return request.question_default if n_hints == 0 else request.question_secondary
        else:
            return request.question_default


class Request:
    def __init__(self, words_2_look_4: tuple, txt_button, question: str, question_alternative=None,
                 request_function=None, interrupt_puzzles_when_activated=False):
        """ object that holds all the information related to each request that can be asked by the participant

        Parameters
        ----------
        words_2_look_4 : Union[Tuple[str, str], Tuple[str], Tuple[str, str], Tuple[str, str], Tuple[str, str], Tuple[str, str], Tuple[str, str], Tuple[str, str], Tuple[str, str], Tuple[str, str], Tuple[str, str]]
        txt_button : str
        question : str
        question_alternative : Union[None, None, str, None, None, None, None, None, None, None, None]
        request_function : method
        interrupt_puzzles_when_activated : bool
        """
        self.participant_might_want_it = False
        self.participant_wants_it = False
        self.question_default = question
        self.question_secondary = question_alternative
        self.key_words = words_2_look_4
        self.request_function = request_function
        self.txt_button = txt_button
        self.interrupt_puzzles_when_activated = interrupt_puzzles_when_activated
        while len(self.txt_button) < 16:
            self.txt_button = ' ' + self.txt_button + ' '

    def process_voice_request(self, speech_recognizer, audio):
        """ processes the audio spoken by the participant (and captured by the 'speech_recognizer') to check if the
        participant asked for this (self) request

        Parameters
        ----------
        speech_recognizer : lib.speech_recognition_module.my_speech_recognition.SpeechRecognizer
        audio : speech_recognition.audio.AudioData
            audio data that contains the request made

        Returns
        -------
        bool
        """
        if speech_recognizer.look_for_words_in_audio(words_2_look_4=self.key_words, audio=audio):
            self.participant_might_want_it = True
            if verbose.VERBOSE.microphone_information:
                print(' [M] participant might want', self.key_words[0])
        return self.participant_might_want_it
