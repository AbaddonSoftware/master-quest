from flask import abort, g, jsonify, request
from src.domain.decorators.decorator import require_permission
from src.domain.security.permissions import Permission
from src.domain.validators import validate_in_enum, validate_int, validate_str
from src.persistence.models import Board

from . import board_bp
from .services import create_board, create_board_column, soft_delete_board, view_board


@board_bp.post("")
@require_permission(Permission.CREATE_BOARD, room="room")
def create_board_route():
    data = request.get_json(silent=True) or {}

    field = "name"
    name = validate_str(data.get(field), field, min_len=3, max_len=30)

    field = "room_id"
    room_id = validate_int(data.get(field), field)
    new_board = create_board(room_id=room_id, name=name)
    return jsonify({"room_id": new_board.room_id, "board_id": new_board.public_id}), 201


@board_bp.delete("/<string:board_id>/soft_delete")
@require_permission(Permission.SOFT_DELETE_BOARD, room="room")
def soft_delete_board_route(board_id):
    soft_delete_board(board_id)
    return jsonify({"message": f"Board '{board_id}' has been soft deleted."}), 200


@board_bp.get("")
@require_permission(Permission.VIEW_BOARD, room="room")
def view_board_route():
    room = request.args.get("room")
    boards = view_board(room)
    return jsonify({"boards": [board.public_id for board in boards]}), 200


@board_bp.post("<string:board_public_id>/columns")
@require_permission(Permission.CREATE_BOARD_COLUMN, room="room")
def create_board_column_route(board_public_id: str):
    data = request.get_json(silent=True) or {}
    field = "title"
    title = ""
    field = "wip_limit"
    wip_limit = ""
    field = "column_type"
    column_type = ""
    try:
        create_board_column(board_public_id, title, wip_limit, column_type)
    except Exception as e:
        return None
