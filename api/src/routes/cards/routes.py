from flask import jsonify, request

from ...domain.decorators import require_permission
from ...domain.security.permissions import Permission
from . import card_bp
from .services import (
    create_card,
    hard_delete_card,
    restore_card,
    soft_delete_card,
    update_card,
)


@card_bp.post("")
@require_permission(Permission.CREATE_CARD)
def create_card_route(room_public_id: str, board_public_id: str, column_id: int):
    data = request.get_json(silent=True) or {}
    card = create_card(
        room_public_id=room_public_id,
        board_public_id=board_public_id,
        column_id=column_id,
        title=data.get("title"),
        description=data.get("description"),
    )
    resp = jsonify(
        {
            "card": {
                "id": str(card.public_id),
                "title": card.title,
                "description": card.description,
                "position": card.position,
                "column_id": card.column_id,
            }
        }
    )
    resp.status_code = 201
    return resp


@card_bp.patch("/<string:card_public_id>")
@require_permission(Permission.EDIT_CARD)
def update_card_route(
    room_public_id: str,
    board_public_id: str,
    column_id: int,
    card_public_id: str,
):
    data = request.get_json(silent=True) or {}
    card = update_card(
        room_public_id=room_public_id,
        board_public_id=board_public_id,
        card_public_id=card_public_id,
        title=data.get("title"),
        description=data.get("description"),
        target_column_id=data.get("column_id", column_id),
    )
    return jsonify(
        {
            "card": {
                "id": str(card.public_id),
                "title": card.title,
                "description": card.description,
                "position": card.position,
                "column_id": card.column_id,
            }
        }
    )


@card_bp.delete("/<string:card_public_id>")
@require_permission(Permission.EDIT_CARD)
def delete_card_route(
    room_public_id: str, board_public_id: str, column_id: int, card_public_id: str
):
    soft_delete_card(
        room_public_id=room_public_id,
        board_public_id=board_public_id,
        card_public_id=card_public_id,
    )
    return jsonify({"message": "Card archived."}), 200


@card_bp.post("/<string:card_public_id>/restore")
@require_permission(Permission.EDIT_CARD)
def restore_card_route(
    room_public_id: str, board_public_id: str, column_id: int, card_public_id: str
):
    card = restore_card(
        room_public_id=room_public_id,
        board_public_id=board_public_id,
        card_public_id=card_public_id,
    )
    return jsonify(
        {
            "card": {
                "id": str(card.public_id),
                "title": card.title,
                "description": card.description,
                "position": card.position,
                "column_id": card.column_id,
            }
        }
    )


@card_bp.delete("/<string:card_public_id>/hard")
@require_permission(Permission.EDIT_CARD)
def hard_delete_card_route(
    room_public_id: str, board_public_id: str, column_id: int, card_public_id: str
):
    hard_delete_card(
        room_public_id=room_public_id,
        board_public_id=board_public_id,
        card_public_id=card_public_id,
    )
    return jsonify({"message": "Card permanently deleted."}), 200
