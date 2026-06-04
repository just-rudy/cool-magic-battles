from enum import Enum


class GameStatus(str, Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class UserRole(str, Enum):
    GUEST = "guest"
    AUTHENTICATED = "authenticated"
    PLAYER = "player"
    MODERATOR = "moderator"
    MASTER = "master"


class CardAction(str, Enum):
    ATTACK = "attack"
    DEF = "defense"
    DRAW = "draw"
    HEAL = "heal"
    HAND_BUFF = "hand_buff"
    ECHO_BUFF = "echo_buff"


class UsePattern(str, Enum):
    REG = "reg"  # regular use, applies effect immediately when played from hand
    DISCARD = (
        "discard"  # discard to apply effect (put in player discard instead of table)
    )
    BANISH = "banish"  # discard comepletely to apply effect, won't be played again in this game  # noqa: E501
    ON_TOP = (
        "on_top"  # put on top of draw deck to apply effect, will be drawn next turn
    )


class DeckType(str, Enum):
    DRAW = "draw"  # player
    HAND = "hand"  # player
    TABLE = "table"  # player
    DISCARD = "discard"  # players deck, will be draw cards later
    MARKET = "market"  # game
    BANISH = "banish"  # game discard deck, will not be played again during the game
    DECK = "deck"  # game
