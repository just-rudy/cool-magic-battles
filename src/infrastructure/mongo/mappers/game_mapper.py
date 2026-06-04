"""Mapper: Game entity ↔ GameDocument."""
from uuid import UUID, uuid4

from domain.entities import Deck, Game, Player
from domain.entities.game import PendingAttack
from domain.enums import DeckType, GameStatus
from infrastructure.mongo.mappers.card_mapper import MongoCardMapper
from infrastructure.mongo.models.game_model import (
    DeckDocument,
    GameDocument,
    PendingAttackDocument,
    PlayerDocument,
)


class MongoGameMapper:
    @staticmethod
    def _pending_attack_to_doc(pa: PendingAttack) -> PendingAttackDocument:
        return PendingAttackDocument(
            attacker_id=str(pa.attacker_id),
            defender_id=str(pa.defender_id),
            damage=pa.damage,
        )

    @staticmethod
    def _pending_attack_from_doc(
        doc: PendingAttackDocument | None,
    ) -> PendingAttack | None:
        if doc is None:
            return None
        return PendingAttack(
            attacker_id=UUID(doc["attacker_id"]),
            defender_id=UUID(doc["defender_id"]),
            damage=doc["damage"],
        )

    @staticmethod
    def _deck_to_doc(deck: Deck) -> DeckDocument:
        return DeckDocument(
            id=str(deck.id),
            type=deck.type.value,
            if_open=deck.if_open,
            cards=[MongoCardMapper.to_document(c) for c in deck.cards],
        )

    @staticmethod
    def _deck_from_doc(doc: DeckDocument) -> Deck:
        return Deck(
            id=UUID(doc["id"]),
            type=DeckType(doc["type"]),
            if_open=doc.get("if_open", False),
            cards=[MongoCardMapper.to_entity(c) for c in doc.get("cards", [])],
        )

    @staticmethod
    def _player_to_doc(player: Player) -> PlayerDocument:
        return PlayerDocument(
            id=str(player.id),
            user_id=str(player.user_id),
            nickname=player.nickname,
            turn_order=player.turn_order,
            health=player.health,
            base_echo=player.base_echo,
            cur_echo=player.cur_echo,
            hand_size=player.hand_size,
            draw_deck=MongoGameMapper._deck_to_doc(player.draw_deck),
            hand_deck=MongoGameMapper._deck_to_doc(player.hand_deck),
            table_deck=MongoGameMapper._deck_to_doc(player.table_deck),
            discard_deck=MongoGameMapper._deck_to_doc(player.discard_deck),
        )

    @staticmethod
    def _player_from_doc(doc: PlayerDocument) -> Player:
        return Player(
            id=UUID(doc["id"]),
            user_id=UUID(doc["user_id"]),
            nickname=doc["nickname"],
            turn_order=doc.get("turn_order", 0),
            health=doc.get("health", 20),
            base_echo=doc.get("base_echo", 0),
            cur_echo=doc.get("cur_echo", 0),
            hand_size=doc.get("hand_size", 5),
            draw_deck=(
                MongoGameMapper._deck_from_doc(doc["draw_deck"])
                if "draw_deck" in doc
                else Deck(id=uuid4(), type=DeckType.DRAW)
            ),
            hand_deck=(
                MongoGameMapper._deck_from_doc(doc["hand_deck"])
                if "hand_deck" in doc
                else Deck(id=uuid4(), type=DeckType.HAND)
            ),
            table_deck=(
                MongoGameMapper._deck_from_doc(doc["table_deck"])
                if "table_deck" in doc
                else Deck(id=uuid4(), type=DeckType.TABLE)
            ),
            discard_deck=(
                MongoGameMapper._deck_from_doc(doc["discard_deck"])
                if "discard_deck" in doc
                else Deck(id=uuid4(), type=DeckType.DISCARD)
            ),
        )

    @staticmethod
    def to_document(game: Game) -> GameDocument:
        doc = GameDocument(
            _id=str(game.id),
            host_user_id=str(game.host_user_id),
            name=game.name,
            status=game.status.value,
            cur_turn=game.cur_turn,
            cur_player_id=str(game.cur_player_id) if game.cur_player_id else None,
            winner_id=str(game.winner_id) if game.winner_id else None,
            market_deck=MongoGameMapper._deck_to_doc(game.market_deck),
            game_deck=MongoGameMapper._deck_to_doc(game.game_deck),
            banish_deck=MongoGameMapper._deck_to_doc(game.banish_deck),
            players=[MongoGameMapper._player_to_doc(p) for p in game.players],
        )
        if game.pending_attack is not None:
            doc["pending_attack"] = MongoGameMapper._pending_attack_to_doc(
                game.pending_attack
            )
        return doc

    @staticmethod
    def to_entity(doc: GameDocument) -> Game:
        return Game(
            id=UUID(doc["_id"]),
            host_user_id=UUID(doc["host_user_id"]),
            name=doc.get("name", ""),
            status=GameStatus(doc["status"]),
            cur_turn=doc.get("cur_turn", 0),
            cur_player_id=(
                UUID(doc["cur_player_id"]) if doc.get("cur_player_id") else None
            ),
            winner_id=UUID(doc["winner_id"]) if doc.get("winner_id") else None,
            pending_attack=MongoGameMapper._pending_attack_from_doc(
                doc.get("pending_attack")
            ),
            market_deck=(
                MongoGameMapper._deck_from_doc(doc["market_deck"])
                if "market_deck" in doc
                else Deck(id=uuid4(), type=DeckType.MARKET, if_open=True)
            ),
            game_deck=(
                MongoGameMapper._deck_from_doc(doc["game_deck"])
                if "game_deck" in doc
                else Deck(id=uuid4(), type=DeckType.DECK)
            ),
            banish_deck=(
                MongoGameMapper._deck_from_doc(doc["banish_deck"])
                if "banish_deck" in doc
                else Deck(id=uuid4(), type=DeckType.BANISH)
            ),
            players=[
                MongoGameMapper._player_from_doc(p)
                for p in doc.get("players", [])
            ],
        )
