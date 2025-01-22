from enum import Enum


class ChinesePokerStatus(Enum):
    START_GAME = "START_GAME"
    START_MATCH = "START_MATCH"
    DEAL_CARDS = "DEAL_CARDS"
    START_ROUND = "START_ROUND"
    START_TURN = "START_TURN"
