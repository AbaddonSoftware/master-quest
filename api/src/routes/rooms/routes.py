from flask import jsonify, request
from ...domain.decorators import require_permission
from ...domain.security.permissions import Permission, RoomType
from ...domain.validators import (
    validate_in_enum,
    validate_str,
    validate_user_logged_in,
)

from . import room_bp
from .services import create_room, view_room, view_rooms, delete_room


@room_bp.post("/rooms")
def create_room_route():
    id = validate_user_logged_in()
    data = request.get_json(silent=True) or {}
    field = "name"
    name = validate_str(data.get(field), field, min_len=3, max_len=30)
    new_room = create_room(creator_user_id=id, name=name)
    return jsonify({"public_id": new_room.public_id, "name": new_room.name}), 201


@room_bp.get("/rooms/<string:room_public_id>")
def view_room_by_public_id(room_public_id: str):
    room = view_room(room_public_id)
    room_data = {
        "public_id": room.public_id,
        "name": room.name,
    }
    return jsonify(room_data), 200


@room_bp.get("/rooms")
def view_rooms_route():
    user_id = validate_user_logged_in()
    rooms = view_rooms(user_id)
    payload = []
    for room in rooms:
        payload.append(
            {
                "public_id": room.public_id,
                "name": room.name,
                "boards": [
                    {
                        "public_id": board.public_id,
                        "name": board.name,
                    }
                    for board in room.boards
                    if not board.deleted_at
                ],
            }
        )
    return jsonify({"rooms": payload}), 200


@room_bp.delete("/rooms/<string:room_public_id>")
def delete_room_route(room_public_id: str):
    user_id = validate_user_logged_in()
    delete_room(room_public_id=room_public_id, actor_user_id=user_id)
    return jsonify({"message": "Room deleted."}), 200
