from flask import jsonify, request
from src.domain.decorators import require_permission
from src.domain.security.permissions import Permission, RoomType
from src.domain.validators import (get_authenticated_user_id, validate_in_enum,
                                   validate_string_field,
                                   validate_string_length)

from . import room_bp
from .services import create_room, view_rooms


@room_bp.post("")
def create_room_route():
    id = get_authenticated_user_id()

    data = request.get_json(silent=True) or {}

    field = "name"
    name = validate_string_field(data.get(field), field)
    validate_string_length(name, 3, 30, field)

    field = "room_type"
    room_type = validate_string_field(data.get(field), field)
    room_type = validate_in_enum(room_type, RoomType, field)

    new_room = create_room(creator_user_id=id, name=name, room_type=room_type)
    return jsonify({"room_id": new_room.public_id}), 201


@room_bp.get("")
def view_rooms_route():
    get_authenticated_user_id()
    rooms = view_rooms()
    return jsonify({"rooms": [room.public_id for room in rooms]}), 200
