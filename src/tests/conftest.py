from typing import Callable
from uuid import UUID, uuid4

import pytest

from domain.entities.card import Card
from domain.entities.deck import Deck
from domain.entities.game import Game
from domain.entities.player import Player
from domain.entities.user import User
from domain.enums import DeckType, GameStatus


@pytest.fixture
def make_card() -> Callable[..., Card]:
    def _make_card(
        *,
        title: str = "Test card",
        creature: str = "test dwarf",
        power: int = 1,
        echo: int = 1,
        cost: int = 3,
    ) -> Card:
        return Card(
            id=uuid4(),
            title=title,
            creature=creature,
            power=power,
            echo=echo,
            cost=cost,
        )

    return _make_card


@pytest.fixture
def make_deck() -> Callable[..., Deck]:
    def _make_deck(
        *,
        type: DeckType = DeckType.DECK,
        if_open: bool = False,
        cards: list[Card] | None = None,
    ) -> Deck:
        return Deck(
            id=uuid4(),
            type=type,
            if_open=if_open,
            cards=cards or [],
        )

    return _make_deck


@pytest.fixture
def make_user() -> Callable[..., User]:
    def _make_user(
        username: str = "user",
    ) -> User:
        return User(
            id=uuid4(),
            username=username,
        )

    return _make_user


@pytest.fixture
def make_player(make_deck: Callable[..., Deck]) -> Callable[..., Player]:
    def _make_player(
        *,
        user_id: UUID | None = None,
        nickname: str = "player",
        turn_order: int = 0,
        health: int = 20,
        base_echo: int = 0,
        cur_echo: int = 0,
        hand_size: int = 5,
        draw_deck: Deck | None = None,
        hand_deck: Deck | None = None,
        table_deck: Deck | None = None,
        discard_deck: Deck | None = None,
    ) -> Player:
        return Player(
            id=uuid4(),
            user_id=user_id or uuid4(),
            nickname=nickname,
            turn_order=turn_order,
            health=health,
            base_echo=base_echo,
            cur_echo=cur_echo,
            hand_size=hand_size,
            draw_deck=draw_deck or make_deck(),
            hand_deck=hand_deck or make_deck(),
            table_deck=table_deck or make_deck(),
            discard_deck=discard_deck or make_deck(),
        )

    return _make_player


@pytest.fixture
def make_game(make_deck: Callable[..., Deck]) -> Callable[..., Game]:
    def _make_game(
        *,
        host_id: UUID,
        status: GameStatus = GameStatus.CREATED,
        players: list[Player] | None = None,
        current_turn: int = 0,
        current_player_id: UUID | None = None,
        market_deck: Deck | None = None,
        game_deck: Deck | None = None,
        banish_deck: Deck | None = None,
    ) -> Game:
        return Game(
            id=uuid4(),
            host_id=host_id or uuid4(),
            status=status,
            players=players or [],
            current_turn=current_turn,
            current_player_id=current_player_id,
            market_deck=market_deck or make_deck(type=DeckType.DECK, if_open=True),
            game_deck=game_deck or make_deck(type=DeckType.DECK, if_open=False),
            banish_deck=banish_deck or make_deck(type=DeckType.DECK, if_open=False),
        )

    return _make_game
