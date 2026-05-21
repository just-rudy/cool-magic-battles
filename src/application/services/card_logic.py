from domain.entities.card import Card
from domain.entities.player import Player


class CardLogic:
    def can_purchase(self, player: Player, card: Card) -> bool:
        return player.cur_echo >= card.cost

    def can_be_played(self, player: Player, card: Card) -> bool:
        return card in player.hand_deck.cards

    # TODO: card_effect
    def apply_effect(
        self,
        player: Player,
        card: Card,
        target: Player | None = None,
    ) -> None:
        player.cur_echo += card.echo
