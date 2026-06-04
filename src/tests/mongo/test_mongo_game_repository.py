"""Tests for MongoGameRepository."""
from uuid import uuid4

import pytest

from domain.entities import Card, Deck, Game, Player
from domain.entities.card_type import CardType
from domain.entities.game import PendingAttack
from domain.entities.image import Image
from domain.enums import CardAction, DeckType, GameStatus, UsePattern
from infrastructure.db.exceptions import EntityNotFoundError
from infrastructure.mongo.repositories.mongo_game_repository import MongoGameRepository


@pytest.fixture
def repo(mongo_db):
    return MongoGameRepository(mongo_db)


def _make_card(title: str = "TestCard") -> Card:
    image = Image(id=uuid4(), title=title, file=f"cards/{title.lower()}.png")
    ct = CardType(
        id=uuid4(),
        action=CardAction.ATTACK,
        usage_pattern=UsePattern.REG,
        color="red",
    )
    return Card(
        id=uuid4(), title=title, creature="Orc",
        card_type_id=ct.id, image_id=image.id,
        power=2, echo=1, cost=3, cool_points=1,
        image=image, card_type=ct,
    )


def _make_player(nickname="player1") -> Player:
    return Player(
        id=uuid4(), user_id=uuid4(), nickname=nickname,
        turn_order=0, health=20, base_echo=0, cur_echo=2, hand_size=5,
        draw_deck=Deck(id=uuid4(), type=DeckType.DRAW, cards=[_make_card("DrawCard")]),
        hand_deck=Deck(id=uuid4(), type=DeckType.HAND, cards=[_make_card("HandCard")]),
        table_deck=Deck(id=uuid4(), type=DeckType.TABLE, cards=[]),
        discard_deck=Deck(id=uuid4(), type=DeckType.DISCARD, cards=[]),
    )


def _make_game(players=None) -> Game:
    return Game(
        id=uuid4(),
        host_user_id=uuid4(),
        status=GameStatus.CREATED,
        players=players or [],
        cur_turn=0,
        market_deck=Deck(
            id=uuid4(), type=DeckType.MARKET, if_open=True,
            cards=[_make_card("MarketCard")]
        ),
        game_deck=Deck(id=uuid4(), type=DeckType.DECK, cards=[]),
        banish_deck=Deck(id=uuid4(), type=DeckType.BANISH, cards=[]),
    )


def test_save_and_get_game(repo):
    game = _make_game()
    repo.save(game)

    result = repo.get(game.id)
    assert result.id == game.id
    assert result.status == GameStatus.CREATED
    assert result.host_user_id == game.host_user_id


def test_get_raises_when_not_found(repo):
    with pytest.raises(EntityNotFoundError):
        repo.get(uuid4())


def test_save_updates_status(repo):
    game = _make_game()
    repo.save(game)

    game.status = GameStatus.IN_PROGRESS
    game.cur_turn = 3
    repo.save(game)

    result = repo.get(game.id)
    assert result.status == GameStatus.IN_PROGRESS
    assert result.cur_turn == 3


def test_delete_game(repo):
    game = _make_game()
    repo.save(game)
    repo.delete(game.id)

    with pytest.raises(EntityNotFoundError):
        repo.get(game.id)


def test_delete_raises_when_not_found(repo):
    with pytest.raises(EntityNotFoundError):
        repo.delete(uuid4())


def test_exists(repo):
    game = _make_game()
    repo.save(game)
    assert repo.exists(game.id) is True
    assert repo.exists(uuid4()) is False


def test_players_are_persisted(repo):
    p1 = _make_player("gandalf")
    p2 = _make_player("saruman")
    game = _make_game(players=[p1, p2])
    repo.save(game)

    result = repo.get(game.id)
    assert len(result.players) == 2
    nicknames = {p.nickname for p in result.players}
    assert nicknames == {"gandalf", "saruman"}


def test_player_decks_are_persisted(repo):
    player = _make_player()
    game = _make_game(players=[player])
    repo.save(game)

    result = repo.get(game.id)
    loaded_player = result.players[0]
    assert len(loaded_player.draw_deck.cards) == 1
    assert loaded_player.draw_deck.cards[0].title == "DrawCard"
    assert len(loaded_player.hand_deck.cards) == 1
    assert loaded_player.hand_deck.cards[0].title == "HandCard"


def test_market_deck_is_persisted(repo):
    game = _make_game()
    repo.save(game)

    result = repo.get(game.id)
    assert len(result.market_deck.cards) == 1
    assert result.market_deck.cards[0].title == "MarketCard"
    assert result.market_deck.if_open is True


def test_pending_attack_is_persisted(repo):
    p1 = _make_player("attacker")
    p2 = _make_player("defender")
    game = _make_game(players=[p1, p2])
    game.status = GameStatus.IN_PROGRESS
    game.pending_attack = PendingAttack(
        attacker_id=p1.id, defender_id=p2.id, damage=5
    )
    repo.save(game)

    result = repo.get(game.id)
    assert result.pending_attack is not None
    assert result.pending_attack.attacker_id == p1.id
    assert result.pending_attack.defender_id == p2.id
    assert result.pending_attack.damage == 5


def test_pending_attack_cleared(repo):
    p1 = _make_player("attacker")
    p2 = _make_player("defender")
    game = _make_game(players=[p1, p2])
    game.pending_attack = PendingAttack(attacker_id=p1.id, defender_id=p2.id, damage=3)
    repo.save(game)

    game.pending_attack = None
    repo.save(game)

    result = repo.get(game.id)
    assert result.pending_attack is None


def test_winner_id_is_persisted(repo):
    player = _make_player()
    game = _make_game(players=[player])
    game.status = GameStatus.FINISHED
    game.winner_id = player.id
    repo.save(game)

    result = repo.get(game.id)
    assert result.winner_id == player.id
    assert result.status == GameStatus.FINISHED


def test_card_type_and_image_preserved_in_deck(repo):
    player = _make_player()
    game = _make_game(players=[player])
    repo.save(game)

    result = repo.get(game.id)
    card = result.players[0].draw_deck.cards[0]
    assert card.image is not None
    assert card.card_type is not None
    assert card.card_type.action == CardAction.ATTACK
