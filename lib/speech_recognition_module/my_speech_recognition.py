import speech_recognition as sr
PROMPT_LIMIT = 3


class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # self.recognizer.dynamic_energy_adjustment_damping = 0.3
        self.mic = sr.Microphone(device_index=1)
        self.stop_listening_command = None      # for listening in background
        with self.mic as source:  # we only need to calibrate once, before start listening
            self.recognizer.adjust_for_ambient_noise(source)
        # print(sr.Microphone.list_microphone_names())

    def listen_with_mic(self, time_limit):
        """ listens with the mic until the time_limit is reached, and returns an audio. If nothing is captured (maximum)
        , time is reached, 'None' is returned.
        is returned.

        Parameters
        ----------
        time_limit : int

        Returns
        -------
        Union[None, speech_recognition.audio.AudioData]
        """
        # Try to capture sound
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source)
            except sr.exceptions.WaitTimeoutError:      # nothing was said
                return None
            return audio

    def recalibrate_mic(self):
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source)

    def listen_in_background(self, callback, calibrate=True, phrase_time_limit=5):
        if calibrate:
            with self.mic as source:                # we only need to calibrate once, before start listening
                self.recognizer.adjust_for_ambient_noise(source)
        # start listening in the background (note that we don't have to do this inside a `with` statement)
        self.stop_listening_command = self.recognizer.listen_in_background(self.mic, callback,
                                                                           phrase_time_limit=phrase_time_limit)

    def stop_listening_in_background(self):
        assert self.stop_listening_command is not None
        self.stop_listening_command()

    def try_to_recognize_sentence(self, audio):
        # set up the response object
        response = {
            "success": True,
            "error": None,
            "transcription": None
        }

        if audio is None:
            response["success"] = True
            response["error"] = "No audio"
            return response

        # Try to recognize
        try:
            response["transcription"] = self.recognizer.recognize_whisper(audio, model="tiny", language="english")
        except sr.RequestError:
            # API was unreachable or unresponsive
            response["success"] = False
            response["error"] = "API unavailable"
        except sr.UnknownValueError:
            # speech was unintelligible
            response["error"] = "Unable to recognize speech"
        except TimeoutError:
            response["success"] = False
            response["error"] = "Connection timed out"
        return response

    def listen_and_recognize_sentence(self, number_attempts=3, time_limit=10, output_source=print):
        text = None
        for j in range(number_attempts):
            print('You can speak!')
            audio = self.listen_with_mic(time_limit=time_limit)
            text = self.try_to_recognize_sentence(audio)
            if text["transcription"]:      # if not None
                print('You said: ', text["transcription"])
                break
            if not text["success"]:
                print('Error ', text['error'])
                break
            output_source("I did not understand. Can you repeat?\n")
        return text['transcription']

    def look_for_words_in_audio(self, words_2_look_4, audio=None):
        """ looks for words to look for (words_2_look_4) in the audio received

        Parameters
        ----------
        audio :
        words_2_look_4 :

        Returns
        -------

        """
        if audio is None:
            audio = self.listen_with_mic(time_limit=3)
        response = self.try_to_recognize_sentence(audio)
        if response['error'] is None:
            recognized_text = response["transcription"]
            if next((word for word in words_2_look_4 if word.lower() in recognized_text.lower()), None) is not None:
                return True
        return False

# if __name__ == "__main__":
#     recognizer = SpeechRecognizer()
#     recognized_text = recognizer.listen_and_recognize_sentence(number_attempts=2)
