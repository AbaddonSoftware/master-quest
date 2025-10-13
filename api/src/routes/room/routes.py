from flask import jsonify, request
from src.domain.decorators import require_permission
from src.domain.security.permissions import Permission, RoomType
from src.domain.validators import (
    validate_in_enum,
    validate_str,
    validate_user_logged_in,
)

from . import room_bp
from .services import create_room, view_rooms


@room_bp.post("")
def create_room_route():
    id = validate_user_logged_in()

    data = request.get_json(silent=True) or {}

    field = "name"
    name = validate_str(data.get(field), field, min_len=3, max_len=30)

    field = "room_type"
    room_type = validate_in_enum(data.get(field), RoomType, field)

    new_room = create_room(creator_user_id=id, name=name, room_type=room_type)
    return jsonify({"room_id": new_room.public_id}), 201


@room_bp.get("")
def view_rooms_route():
    validate_user_logged_in()
    rooms = view_rooms()
    return jsonify({"rooms": [room.public_id for room in rooms]}), 200
