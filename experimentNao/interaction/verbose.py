class VerboseLevels:
    def __init__(self, basic_info, rewards_information, helping_information, microphone_information,
                 feedback_information):
        """ Verbose level of the output to the console from the interaction manager

        Parameters
        ----------
        basic_info : bool
        rewards_information : bool
        helping_information : bool
        microphone_information : bool
        feedback_information : bool
        """
        self.basic_info = basic_info
        self.rewards_information = rewards_information
        self.helping_information = helping_information
        self.microphone_information = microphone_information
        self.feedback_information = feedback_information


VERBOSE = VerboseLevels(basic_info=True, rewards_information=True, helping_information=True,
                        microphone_information=True, feedback_information=True)
# VERBOSE = VerboseLevels(puzzle_numbers=True, rewards_information=False, helping_information=False,
#                         microphone_information=True, feedback_information=False)

