import base64

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from application.controllers.user_controller import UserController
from application.services.card_factory import generate_cards, list_card_types
from domain.enums import UserRole
from infrastructure.db.models import CardModel, CardTypeModel, ImageModel
from infrastructure.db.repositories.sqlalchemy_user_repository import (
    SqlAlchemyUserRepository,
)


def _seed_one_card(session: Session) -> str:
    card = generate_cards(1)[0]
    assert card.image is not None
    card_type = next(ct for ct in list_card_types() if ct.id == card.card_type_id)
    session.add(
        ImageModel(
            id=card.image.id,
            title=card.image.title,
            file=card.image.file,
        )
    )
    session.add(
        CardTypeModel(
            id=card_type.id,
            action=card_type.action.value,
            usage_pattern=card_type.usage_pattern.value,
            if_permanent=card_type.if_permanent,
            color=card_type.color,
        )
    )
    session.add(
        CardModel(
            id=card.id,
            title=card.title,
            creature=card.creature,
            card_type_id=card.card_type_id,
            image_id=card.image_id,
            power=card.power,
            echo=card.echo,
            cost=card.cost,
            cool_points=card.cool_points,
        )
    )
    session.commit()
    return str(card.id)


def test_upload_card_image(client: TestClient, session: Session) -> None:
    card_id = _seed_one_card(session)

    controller = UserController(SqlAlchemyUserRepository(session))
    master = controller.register_user("img_master", "secret12")
    master = controller.update_user_role(master.id, UserRole.MASTER)
    guest = controller.register_user("img_guest", "secret12")

    payload = {
        "title": "Test card",
        "filename": "test.png",
        "content_base64": base64.b64encode(b"png-bytes").decode("ascii"),
        "content_type": "image/png",
    }

    denied = client.post(
        f"/api/v1/cards/{card_id}/image",
        json=payload,
        headers={"X-User-Id": str(guest.id)},
    )
    assert denied.status_code == 403

    allowed = client.post(
        f"/api/v1/cards/{card_id}/image",
        json=payload,
        headers={"X-User-Id": str(master.id)},
    )
    assert allowed.status_code == 200, allowed.text
    assert allowed.json()["image"] is not None


def test_master_can_create_update_and_delete_card(
    client: TestClient, session: Session
) -> None:
    card_id = _seed_one_card(session)

    controller = UserController(SqlAlchemyUserRepository(session))
    master = controller.register_user("catalog_master", "secret12")
    master = controller.update_user_role(master.id, UserRole.MASTER)
    guest = controller.register_user("catalog_guest", "secret12")

    card_type_id = str(session.query(CardTypeModel).first().id)  # type: ignore[union-attr]

    create_payload = {
        "title": "New Catalog Card",
        "creature": "Wizard",
        "card_type_id": card_type_id,
        "power": 2,
        "echo": 1,
        "cost": 3,
        "cool_points": 1,
    }

    denied_create = client.post(
        "/api/v1/cards",
        json=create_payload,
        headers={"X-User-Id": str(guest.id)},
    )
    assert denied_create.status_code == 403

    created = client.post(
        "/api/v1/cards",
        json=create_payload,
        headers={"X-User-Id": str(master.id)},
    )
    assert created.status_code == 201, created.text
    new_card_id = created.json()["id"]
    assert created.json()["title"] == "New Catalog Card"

    update_payload = {
        **create_payload,
        "title": "Updated Catalog Card",
        "power": 4,
    }

    updated = client.put(
        f"/api/v1/cards/{new_card_id}",
        json=update_payload,
        headers={"X-User-Id": str(master.id)},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["title"] == "Updated Catalog Card"
    assert updated.json()["power"] == 4

    deleted = client.delete(
        f"/api/v1/cards/{new_card_id}",
        headers={"X-User-Id": str(master.id)},
    )
    assert deleted.status_code == 204

    still_there = client.get(f"/api/v1/cards/{card_id}")
    assert still_there.status_code == 200
