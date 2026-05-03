from rich.panel import Panel
from rich.text import Text


def print_menu() -> Panel:

    body = Text()
    body.append(" TECH UI\n", style="bold orange1")

    # reg
    body.append("reg ", style="bold purple")
    body.append("{username}", style="cyan")
    body.append(": to reg a new user\n")

    # new
    body.append("new", style="bold purple")
    body.append(": to create a new game\n")

    # login
    body.append("login ", style="bold purple")
    body.append("{user} {game_id?}", style="cyan")
    body.append(": switch current user/player\n")

    # gen_decks
    body.append("gen_decks ", style="bold purple")
    body.append("{game_id?}", style="cyan")
    body.append(": to generate game decks\n")

    # run
    body.append("run ", style="bold purple")
    body.append("{game_id?}", style="cyan")
    body.append(": to run game\n")

    # join
    body.append("join ", style="bold purple")
    body.append("{user?}", style="cyan")
    body.append(": to add a player to the game\n")

    # game
    body.append("game ", style="bold purple")
    body.append("{game_id?}", style="cyan")
    body.append(": show game status\n")

    # play
    body.append("play ", style="bold purple")
    body.append("{card_id|title}", style="cyan")
    body.append(": to play card\n")

    # buy
    body.append("buy ", style="bold purple")
    body.append("{card_id|title}", style="cyan")
    body.append(": to buy card\n")

    # end
    body.append("end", style="bold purple")
    body.append(": to end turn\n")

    # hand
    body.append("hand ", style="bold purple")
    body.append("{player?}", style="cyan")
    body.append(": show hand\n")

    # draw
    body.append("draw ", style="bold purple")
    body.append("{player?}", style="cyan")
    body.append(": show draw deck\n")

    # discard
    body.append("discard ", style="bold purple")
    body.append("{player?}", style="cyan")
    body.append(": show discard deck\n")

    # market
    body.append("market ", style="bold purple")
    body.append("{game_id?}", style="cyan")
    body.append(": show market cards\n")

    # all
    body.append("all", style="bold purple")
    body.append(": show all cards\n")

    # users
    body.append("users", style="bold purple")
    body.append(": show all users\n")

    # players
    body.append("players ", style="bold purple")
    body.append("{game_id?}", style="cyan")
    body.append(": show all players in a game\n")

    # current
    body.append("cur_u", style="bold purple")
    body.append(": show current user\n")

    body.append("cur_p", style="bold purple")
    body.append(": show current player\n")

    body.append("cur_g", style="bold purple")
    body.append(": show current game\n")

    # menu
    body.append("menu", style="bold purple")
    body.append(": print menu\n")

    # exit
    body.append("ext", style="bold purple")
    body.append(": to exit game")

    return Panel(body, border_style="orange1", expand=False)
