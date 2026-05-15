from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_game_service
from application.dto.requests import (
    BuyCardRequest,
    CreateGameRequest,
    FinishGameRequest,
    EndTurnRequest,
    JoinGameRequest,
    PlayCardRequest,
)
from application.dto.responses import (
    CardResponse,
    GameResponse,
    PlayerResponse,
    WinnerResponse,
)
from application.services.game_service import GameAppService
from domain.entities import Card, Game, Player
from domain.enums import GameStatus
from infrastructure.db.exceptions import EntityNotFoundError

router = APIRouter()


def build_card_response(card: Card) -> CardResponse:
    return CardResponse(
        id=card.id,
        title=card.title,
        creature=card.creature,
        power=card.power,
        echo=card.echo,
        cost=card.cost,
        cool_points=card.cool_points,
    )


def build_player_response(player: Player) -> PlayerResponse:
    cards = [
        *player.draw_deck.cards,
        *player.hand_deck.cards,
        *player.table_deck.cards,
        *player.discard_deck.cards,
    ]

    return PlayerResponse(
        id=player.id,
        user_id=player.user_id,
        nickname=player.nickname,
        turn_order=player.turn_order,
        health=player.health,
        base_echo=player.base_echo,
        cur_echo=player.cur_echo,
        hand_size=player.hand_size,
        hand=[build_card_response(card) for card in player.hand_deck.cards],
        table=[build_card_response(card) for card in player.table_deck.cards],
        discard=[build_card_response(card) for card in player.discard_deck.cards],
        draw_count=len(player.draw_deck.cards),
        cool_points=sum(card.cool_points for card in cards),
        cards_count=len(cards),
    )


def build_winner_response(game: Game) -> WinnerResponse | None:
    if game.winner_id is None:
        return None

    winner = next(
        (player for player in game.players if player.id == game.winner_id), None
    )
    if winner is None:
        return None

    cards = [
        *winner.draw_deck.cards,
        *winner.hand_deck.cards,
        *winner.table_deck.cards,
        *winner.discard_deck.cards,
    ]

    return WinnerResponse(
        player_id=winner.id,
        nickname=winner.nickname,
        cool_points=sum(card.cool_points for card in cards),
        cards_count=len(cards),
    )


def build_game_response(game: Game) -> GameResponse:
    return GameResponse(
        id=game.id,
        status=game.status.value,
        cur_turn=game.cur_turn,
        cur_player_id=game.cur_player_id,
        winner=build_winner_response(game),
        players=[build_player_response(player) for player in game.players],
        market=[build_card_response(card) for card in game.market_deck.cards],
        banish_count=len(game.banish_deck.cards),
        deck_count=len(game.game_deck.cards),
    )


@router.get(
    "/{game_id}",
    response_model=GameResponse,
)
def get_game(
    game_id: UUID,
    service: Annotated[GameAppService, Depends(get_game_service)],
) -> GameResponse:
    try:
        game = service.get_game(game_id)
    except EntityNotFoundError as ex:
        raise HTTPException(
            status_code=404,
            detail="Game not found",
        ) from ex

    return build_game_response(game)


@router.post(
    "/new",
    response_model=GameResponse,
)
def create_game(
    request: CreateGameRequest,
    service: Annotated[GameAppService, Depends(get_game_service)],
) -> GameResponse:
    try:
        game = service.create_new_game(request)
        return build_game_response(game)
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex)) from ex


@router.post(
    "/{game_id}/join",
    response_model=GameResponse,
)
def join_game(
    game_id: UUID,
    request: JoinGameRequest,
    service: Annotated[GameAppService, Depends(get_game_service)],
) -> GameResponse:
    try:
        game = service.join_game(game_id, request.user_id)
        return build_game_response(game)
    except EntityNotFoundError as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex)) from ex


@router.get(
    "/{game_id}/players/{player_id}/cards",
    response_model=list[CardResponse],
)
def get_player_cards(
    game_id: UUID,
    player_id: UUID,
    service: Annotated[GameAppService, Depends(get_game_service)],
) -> list[CardResponse]:
    try:
        game = service.get_game(game_id)
    except EntityNotFoundError as ex:
        raise HTTPException(status_code=404, detail="Game not found") from ex

    if game.status != GameStatus.FINISHED:
        raise HTTPException(
            status_code=400,
            detail="Cards are available only after the game is finished",
        )

    player = next((player for player in game.players if player.id == player_id), None)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found in game")

    cards = [
        *player.draw_deck.cards,
        *player.hand_deck.cards,
        *player.table_deck.cards,
        *player.discard_deck.cards,
    ]

    return [build_card_response(card) for card in cards]


@router.post(
    "/{game_id}/start",
    response_model=GameResponse,
)
def start_game(
    game_id: UUID,
    service: Annotated[GameAppService, Depends(get_game_service)],
) -> GameResponse:
    try:
        game = service.start_game(game_id)
        return build_game_response(game)
    except EntityNotFoundError as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex)) from ex


@router.post(
    "/{game_id}/play",
    response_model=GameResponse,
)
def play_card(
    game_id: UUID,
    request: PlayCardRequest,
    service: Annotated[GameAppService, Depends(get_game_service)],
) -> GameResponse:
    try:
        game = service.play_card(
            game_id=game_id,
            player_id=request.player_id,
            card_id=request.card_id,
        )

        return build_game_response(game)
    except EntityNotFoundError as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex)) from ex


@router.post(
    "/{game_id}/buy",
    response_model=GameResponse,
)
def buy_card(
    game_id: UUID,
    request: BuyCardRequest,
    service: Annotated[GameAppService, Depends(get_game_service)],
) -> GameResponse:
    try:
        game = service.buy_card(
            game_id=game_id,
            player_id=request.player_id,
            card_id=request.card_id,
        )

        return build_game_response(game)
    except EntityNotFoundError as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex)) from ex


@router.post(
    "/{game_id}/end-turn",
    response_model=GameResponse,
)
def end_turn(
    game_id: UUID,
    request: EndTurnRequest,
    service: Annotated[GameAppService, Depends(get_game_service)],
) -> GameResponse:
    try:
        game = service.end_turn(
            game_id=game_id,
            player_id=request.player_id,
        )

        return build_game_response(game)
    except EntityNotFoundError as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex)) from ex


@router.post(
    "/{game_id}/finish",
    response_model=GameResponse,
)
def finish_game(
    game_id: UUID,
    request: FinishGameRequest,
    service: Annotated[GameAppService, Depends(get_game_service)],
) -> GameResponse:
    try:
        game = service.finish_game(
            game_id=game_id,
            player_id=request.player_id,
        )

        return build_game_response(game)
    except EntityNotFoundError as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex)) from ex
