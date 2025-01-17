from enum import Enum


class ComplexMovements(Enum):   # Reward (entertaining) movements
    PLAY_GUITAR = 1
    DANCE = 2
    PICTURE = 3
    ELEPHANT = 4
    TAI_CHI = 5


class BodyMovements(Enum):  # 'me', 'you', 'yes', 'no', 'you know what'
    ME = 1
    YOU = 2
    YES = 3
    NO = 4
    YOU_KNOW_WHAT = 5
    EXPLAIN = 6
    EXCITED = 7
    HELLO = 8
