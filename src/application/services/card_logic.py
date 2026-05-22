from __future__ import annotations

from domain.entities.card import Card
from domain.entities.card_type import CardType
from domain.entities.player import Player
from domain.enums import CardAction, UsePattern


class CardLogic:
    def can_purchase(self, player: Player, card: Card) -> bool:
        return player.cur_echo >= card.cost

    def can_be_played(self, player: Player, card: Card) -> bool:
        return card in player.hand_deck.cards

    def can_defend(self, player: Player, card: Card, card_type: CardType) -> bool:
        """Карту защиты можно сыграть только вне своего хода."""
        if card_type.action != CardAction.DEF:
            return False
        if card_type.usage_pattern == UsePattern.DISCARD:
            return card in player.hand_deck.cards
        if card_type.usage_pattern == UsePattern.ON_TOP:
            return card in player.hand_deck.cards
        return False

    def apply_effect(
        self,
        player: Player,
        card: Card,
        card_type: CardType | None = None,
        target: Player | None = None,
        deck_service: object | None = None,
    ) -> int:
        """Применяет эффект карты. Возвращает урон для ATTACK (до применения),
        0 для всех остальных действий."""
        # Всегда добавляем эхо
        player.cur_echo += card.echo

        if card_type is None:
            return 0

        action = card_type.action

        if action == CardAction.ATTACK:
            if target is None:
                raise ValueError("ATTACK card requires a target player")
            # Урон не применяется здесь — возвращается как pending_damage
            # чтобы цель могла защититься. Применение — в game_logic.
            return card.power

        if action == CardAction.HEAL:
            if target is None:
                raise ValueError("HEAL card requires a target player")
            target.health = min(target.health + card.power, 20)

        elif action == CardAction.DEF:
            # DEF применяется через apply_defense, не здесь
            pass

        elif action == CardAction.DRAW:
            if deck_service is not None:
                available = len(player.draw_deck.cards)
                num = min(card.power, available)
                if num > 0:
                    drawn = deck_service.draw(player.draw_deck, num)  # type: ignore[union-attr]
                    player.hand_deck.cards.extend(drawn)

        elif action == CardAction.HAND_BUFF:
            player.hand_size += card.power

        elif action == CardAction.ECHO_BUFF:
            player.base_echo += card.power

        return 0

    def apply_defense(
        self,
        defender: Player,
        card: Card,
        card_type: CardType,
        incoming_damage: int,
    ) -> int:
        """Применяет защитный эффект карты. Возвращает оставшийся урон после защиты.
        Перемещает карту согласно usage_pattern."""
        defender.cur_echo += card.echo

        remaining = max(0, incoming_damage - card.power)

        if card_type.usage_pattern == UsePattern.DISCARD:
            defender.hand_deck.cards.remove(card)
            defender.discard_deck.cards.append(card)
        elif card_type.usage_pattern == UsePattern.ON_TOP:
            defender.hand_deck.cards.remove(card)
            defender.draw_deck.cards.insert(0, card)

        return remaining
