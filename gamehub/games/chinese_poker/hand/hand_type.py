from enum import Enum


class HandType(int, Enum):
    STRAIGHT = 1
    FLUSH = 2
    FULL_HOUSE = 3
    FOUR_OF_A_KIND = 4
    STRAIGHT_FLUSH = 5
