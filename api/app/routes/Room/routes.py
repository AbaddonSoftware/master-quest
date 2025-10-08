from flask import request, g, abort, jsonify
from . import room_bp
from .services import create_room
from app.domain.security.permissions import RoomType
from app.domain.validators import (
    get_authenticated_user_id,
    require_field,
    validate_enum,
    validate_str_length,
)


@room_bp.post("")
def create_room_route():
    id = get_authenticated_user_id()

    data = request.get_json(silent=True) or {}

    field = "name"
    name = require_field(data.get(field), field)
    validate_str_length(name, 3, 30, field)

    field = "room_type"
    room_type = require_field(data.get(field), field)
    room_type = validate_enum(room_type, RoomType, field)

    new_room = create_room(creator_user_id=id, name=name, room_type=room_type)
    return jsonify({"room_id": new_room.public_id}), 201
