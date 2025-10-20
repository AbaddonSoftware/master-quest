from flask import jsonify, request, url_for
from src.domain.decorators.decorator import require_permission
from src.domain.security.permissions import Permission
from src.persistence.models import Board

from . import board_bp
from .services import create_board, create_board_column, soft_delete_board, view_board


@board_bp.post("/rooms/<string:room_public_id>/boards")
@require_permission(Permission.CREATE_BOARD)
def create_board_route(room_public_id: str):
    data = request.get_json(silent=True) or {}
    raw_name = data.get("name")
    board = create_board(room_public_id=room_public_id, name=raw_name)
    resp = jsonify(
        {
            "room_id": room_public_id,
            "board_id": board.public_id,
            "name": board.name,
        }
    )
    resp.status_code = 201
    resp.headers["Location"] = url_for(
        "boards.get_board", board_public_id=board.public_id
    )
    return resp


@board_bp.delete("/<string:board_id>")
@require_permission(Permission.SOFT_DELETE_BOARD)
def soft_delete_board_route(board_id):
    soft_delete_board(board_id)
    return jsonify({"message": f"Board '{board_id}' has been soft deleted."}), 200


@board_bp.get("")
@require_permission(Permission.VIEW_BOARD)
def view_board_route():
    room = request.args.get("room")
    boards = view_board(room)
    return jsonify({"boards": [board.public_id for board in boards]}), 200


@board_bp.post("<string:board_public_id>/columns")
@require_permission(Permission.CREATE_BOARD_COLUMN)
def create_board_column_route(board_public_id: str):
    pass

