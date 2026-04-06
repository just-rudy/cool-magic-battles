from enum import Enum

class GameStatus(str, Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"

class CardType(str, Enum):
    ATTACK = "attack"
    DEFENSE = "defense"
    DRAW = "draw"
    HEAL = "heal"
    HAND_BUFF = "hand_buff"
    ECHO_BUFF = "echo_buff"

class DeckType(str, Enum):
    DRAW = "draw"       # player
    HAND = "hand"       # player
    TABLE = "table"     # player
    DISCARD = "discard" # players deck, will be draw cards later
    MARKET = "market"   # game
    BANISH = "banish"   # game discard deck, will not be played again during the game
    DECK = "deck"       # game