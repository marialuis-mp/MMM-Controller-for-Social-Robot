from functools import wraps
from types import FunctionType

from experimentNao import client
from experimentNao.generated import nao_pb2
import time
import PIL.Image as Image
from experimentNao.interaction.nao_behaviour.requests_enums import ComplexMovements, BodyMovements


def wrapper(method):
    """ avoids error from server causing a crash in the interaction

    Parameters
    ----------
    method : function

    Returns
    -------
    function
    """
    @wraps(method)
    def wrapped(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        except Exception as err:
            print(err)

    return wrapped


class PrintExceptionsAndContinue(type):
    def __new__(meta, classname, bases, class_dict):
        """ avoids error from server causing a crash in the interaction

        Parameters
        ----------
        classname : str
        bases : Tuple
        class_dict : Dict[str, str]
        """
        new_class_dict = {}

        for attribute_name, attribute in class_dict.items():
            if isinstance(attribute, FunctionType):
                # replace it with a wrapped version
                attribute = wrapper(attribute)

            new_class_dict[attribute_name] = attribute

        return type.__new__(meta, classname, bases, new_class_dict)


class NaoClient(metaclass=PrintExceptionsAndContinue):
    def __init__(self):
        """ client that communicates with the Nao server

        """
        self.the_client = client.initialize_client()

    def change_speed_of_speech(self, speed: int):
        """ changes the speed of the speech

        Parameters
        ----------
        speed : int
        """
        number_message = nao_pb2.NumericRequest()
        number_message.number1 = speed
        self.the_client.ChangeSpeechSpeed(number_message)    
    
    def make_nao_say_something(self, text, animated_text=False):
        """ makes Nao speak the argument "text"

        Parameters
        ----------
        text : str
            text to be spoken
        animated_text : bool
            whether the text should be accompanied by gestures
        """
        request_message = nao_pb2.MessageToSpeak()
        request_message.message = text
        request_message.animated_message = animated_text
        self.the_client.SaySomething(request_message)
    
    def make_body_movement(self, movement_type, async_):
        """ makes Nao perform a body movement

        Parameters
        ----------
        movement_type : experimentNao.interaction.nao_behaviour.requests_enums.BodyMovements
        async_ : bool
        """
        assert isinstance(movement_type, BodyMovements)
        possible_requests = (Request(BodyMovements.ME, 'me'),
                             Request(BodyMovements.YOU, 'you'),
                             Request(BodyMovements.YES, 'yes'),
                             Request(BodyMovements.NO, 'no'),
                             Request(BodyMovements.YOU_KNOW_WHAT, 'you know what'),
                             Request(BodyMovements.EXPLAIN, 'explain'),
                             Request(BodyMovements.EXCITED, 'excited'),
                             Request(BodyMovements.HELLO, 'hello'))
        request = nao_pb2.BodyMovement()
        request.movement_tag = get_request_string(possible_requests, movement_type)
        request.asynchronous = async_
        self.the_client.RunBodyMovement(request)
    
    def make_a_coordinated_movement(self, movement_name: ComplexMovements):
        """ makes Nao perform a complex movement (the movements used for the rewards)

        Parameters
        ----------
        movement_name : ComplexMovements
        """
        assert isinstance(movement_name, ComplexMovements)
        possible_requests = (Request(ComplexMovements.PLAY_GUITAR, 'play the guitar'),
                             Request(ComplexMovements.DANCE, 'dance disco'),
                             Request(ComplexMovements.PICTURE, 'take picture'),
                             Request(ComplexMovements.ELEPHANT, 'elephant'),
                             Request(ComplexMovements.TAI_CHI, 'tai chi'))
        movement = nao_pb2.CoordinatedMovement()
        movement.movement = get_request_string(possible_requests, movement_name)
        self.the_client.RunCoordinatedMovement(movement)

    def get_images_from_nao(self):
        """ gets images from the Nao camera

        """
        request_void = nao_pb2.Void()
        image_response = self.the_client.GetCameraCapture(request_void)
        img = Image.frombytes('RGB', (image_response.width, image_response.height), image_response.bytes_image)
        img.show()

    def start_face_detection(self):
        """ starts the face detection module embedded in the Nao robot

        """
        request_void = nao_pb2.Void()
        for i in range(3):
            response3 = self.the_client.StartFaceDetection(request_void)
            time.sleep(1)


def get_request_string(array_of_requests, enum):
    """ returns the correct type of request depending on the

    Parameters
    ----------
    array_of_requests : list
        the list of all the requests allowed for a specific group of requests
    enum : Enum
        variable of type enum, that corresponds to a request

    Returns
    -------

    """
    return next((req.request_string for req in array_of_requests if req.request_enum == enum))


class Request:
    def __init__(self, req_enum, req_string):
        """ request

        Parameters
        ----------
        req_enum : Enum
        req_string : str
        """
        self.request_string = req_string
        self.request_enum = req_enum


def interaction_example():
    """ small showcase of the usage of the client

    """
    nao_client = NaoClient()
    nao_client.make_nao_say_something('hello')
    nao_client.get_images_from_nao()
    nao_client.make_nao_say_something('see you later')
