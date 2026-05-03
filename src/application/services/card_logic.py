from domain.entities.card import Card
from domain.entities.player import Player


class CardLogic:
    def can_purchase(self, player: Player, card: Card) -> bool:
        # temporary
        sum_echo = player.cur_echo + player.base_echo
        return sum_echo >= card.cost

    def can_be_played(self, player: Player, card: Card) -> bool:
        return card in player.hand_deck.cards

    # TODO: card_effect
    def apply_effect(self, player: Player, card: Card) -> None:
        player.cur_echo += card.echo
