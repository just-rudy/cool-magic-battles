from domain.enums import CardAction

ACTION_COLORS: dict[CardAction, str] = {
    CardAction.ATTACK: "red",
    CardAction.HEAL: "green",
    CardAction.DRAW: "purple",
    CardAction.DEF: "blue",
    CardAction.HAND_BUFF: "yellow",
    CardAction.ECHO_BUFF: "pink",
}


def color_for_action(action: CardAction) -> str:
    return ACTION_COLORS[action]
