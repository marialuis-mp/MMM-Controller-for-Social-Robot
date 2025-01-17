from experimentNao.interaction import interaction_manager


class InteractionSettings:
    def __init__(self, interaction_mode, demo: bool, with_nao: bool, say_hello: bool, speak_instructions: bool,
                 ask_for_feedback: bool, save_excel: bool, second_screen: bool, lichess_db: bool):
        """

        Parameters
        ----------
        interaction_mode : experimentNao.interaction.interaction_manager.InteractionMode
            the type of the session
        demo : bool
            True if this is the tryout quick session for 1st time participants, or False if it is the normal interaction
        with_nao : bool
            True if nao is connected to the interaction, or False if the interaction is done without Nao
        say_hello : bool
            whether Nao should introduce the interaction
        speak_instructions : bool
            whether Nao should state the instructions at the beginning
        ask_for_feedback : bool
            whether to pose the questions about beliefs, goals, and emotions to the participants
        save_excel : bool
            if the Excel should be saved or not
        second_screen : bool
            if the chess games should appear on the second screen
        lichess_db : bool
            use the full database of chess puzzles
        """
        self.interaction_mode = interaction_mode
        self.demo = demo
        self.with_nao = with_nao
        self.say_hello = say_hello
        self.speak_instructions = speak_instructions
        self.ask_for_feedback = ask_for_feedback
        self.save_excel = save_excel
        self.second_screen = second_screen
        self.lichess_db = lichess_db
        self.session_number = 1

    def set_settings_demo(self):
        """
        set the settings needed in the demo mode

        """
        self.demo = True
        self.with_nao = True
        self.say_hello = True
        self.speak_instructions = True
        self.ask_for_feedback = True
        self.save_excel = False
        self.second_screen = True
        self.lichess_db = False

    def set_settings_training_1st(self):
        """
        set the settings needed for the 1st interaction (training)

        """
        self.set_settings_with_participant(speak_instructions=False)
        self.interaction_mode = interaction_manager.InteractionMode.TRAINING
        self.demo = False
        self.say_hello = False
        self.session_number = 1

    def set_settings_training_2nd(self):
        """
        set the settings needed for the 2nd interaction (training)

        """
        self.set_settings_with_participant(speak_instructions=True)
        self.interaction_mode = interaction_manager.InteractionMode.TRAINING
        self.demo = False
        self.session_number = 2

    def set_settings_mbc(self):
        """
        set the settings needed for the 3rd interaction (mbc part)

        """
        self.set_settings_with_participant(speak_instructions=False)
        self.interaction_mode = interaction_manager.InteractionMode.MBC
        self.demo = False

    def set_settings_alternative(self):
        """
        set the settings needed for the 3rd interaction (alternative controller part)

        """
        self.set_settings_with_participant(speak_instructions=False)
        self.interaction_mode = interaction_manager.InteractionMode.ALTERNATIVE_C
        self.demo = False

    def set_settings_with_participant(self, speak_instructions=True):
        """
        set the settings needed for any training session

        """
        self.with_nao = True
        self.say_hello = True
        self.speak_instructions = speak_instructions
        self.ask_for_feedback = True
        self.save_excel = True
        self.second_screen = True
        self.lichess_db = True
