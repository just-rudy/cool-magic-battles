from uuid import uuid4

from sqlalchemy.orm import Session

from domain.entities import Card, Game, Image, Player, User
from domain.enums import DeckType, GameStatus
from infrastructure.db.models import DeckCardModel, DeckModel
from infrastructure.db.repositories.sqlalchemy_game_repository import (
    SqlAlchemyGameRepository,
)
from infrastructure.db.repositories.sqlalchemy_user_repository import (
    SqlAlchemyUserRepository,
)


def make_image(title: str) -> Image:
    return Image(
        id=uuid4(),
        title=title,
        file=f"cards/{title.lower()}.png",
    )


def test_save_and_get_game_with_players(session: Session) -> None:
    user_repo = SqlAlchemyUserRepository(session)
    game_repo = SqlAlchemyGameRepository(session)

    host = User(id=uuid4(), username="host")
    guest = User(id=uuid4(), username="guest")
    user_repo.save(host)
    user_repo.save(guest)

    game = Game(id=uuid4(), host_user_id=host.id, status=GameStatus.CREATED)
    game.players.append(
        Player(id=uuid4(), user_id=host.id, nickname="host", turn_order=0)
    )
    game.players.append(
        Player(id=uuid4(), user_id=guest.id, nickname="guest", turn_order=1)
    )

    game_repo.save(game)
    loaded = game_repo.get(game.id)

    assert loaded.id == game.id
    assert len(loaded.players) == 2
    assert loaded.players[0].nickname == "host"


def test_save_and_get_game_with_winner(session: Session) -> None:
    user_repo = SqlAlchemyUserRepository(session)
    game_repo = SqlAlchemyGameRepository(session)

    host = User(id=uuid4(), username="host")
    guest = User(id=uuid4(), username="guest")
    user_repo.save(host)
    user_repo.save(guest)

    winner = Player(id=uuid4(), user_id=host.id, nickname="host", turn_order=0)
    loser = Player(id=uuid4(), user_id=guest.id, nickname="guest", turn_order=1)
    game = Game(
        id=uuid4(),
        host_user_id=host.id,
        status=GameStatus.FINISHED,
        winner_id=winner.id,
    )
    game.players.extend([winner, loser])

    game_repo.save(game)
    loaded = game_repo.get(game.id)

    assert loaded.winner_id == winner.id


def test_save_and_get_game_with_decks_and_cards(session: Session) -> None:
    user_repo = SqlAlchemyUserRepository(session)
    game_repo = SqlAlchemyGameRepository(session)

    host = User(id=uuid4(), username="host")
    user_repo.save(host)

    game = Game(id=uuid4(), host_user_id=host.id, status=GameStatus.IN_PROGRESS)
    player = Player(id=uuid4(), user_id=host.id, nickname="host", turn_order=0)
    game.players.append(player)
    game.cur_player_id = player.id

    market_image = make_image("Market")
    hand_image = make_image("Hand")
    draw_image = make_image("Draw")
    market_card = Card(
        id=uuid4(),
        title="Market",
        creature="Wizard",
        card_type_id=uuid4(),
        image_id=market_image.id,
        image=market_image,
        cost=2,
        echo=1,
    )
    hand_card = Card(
        id=uuid4(),
        title="Hand",
        creature="Knight",
        card_type_id=uuid4(),
        image_id=hand_image.id,
        image=hand_image,
        cost=1,
        echo=2,
    )
    draw_card = Card(
        id=uuid4(),
        title="Draw",
        creature="Dragon",
        card_type_id=uuid4(),
        image_id=draw_image.id,
        image=draw_image,
        cost=3,
        echo=0,
    )

    game.market_deck.type = DeckType.MARKET
    game.market_deck.cards = [market_card]
    player.hand_deck.type = DeckType.HAND
    player.hand_deck.cards = [hand_card]
    player.draw_deck.type = DeckType.DRAW
    player.draw_deck.cards = [draw_card]
    player.table_deck.type = DeckType.TABLE
    player.discard_deck.type = DeckType.DISCARD

    game_repo.save(game)

    deck_models = session.query(DeckModel).filter(DeckModel.game_id == game.id).all()
    assert len(deck_models) == 7
    assert {deck.type for deck in deck_models if deck.player_id is None} == {
        DeckType.MARKET.value,
        DeckType.DECK.value,
        DeckType.BANISH.value,
    }
    assert {deck.type for deck in deck_models if deck.player_id == player.id} == {
        DeckType.DRAW.value,
        DeckType.HAND.value,
        DeckType.TABLE.value,
        DeckType.DISCARD.value,
    }
    assert session.query(DeckCardModel).count() == 3

    loaded = game_repo.get(game.id)

    assert loaded.market_deck.cards[0].title == "Market"
    assert loaded.market_deck.cards[0].image is not None
    assert loaded.players[0].hand_deck.cards[0].title == "Hand"
    assert loaded.players[0].draw_deck.cards[0].title == "Draw"
