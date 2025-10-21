from flask import jsonify, request, url_for

from ...domain.decorators import require_permission
from ...domain.security.permissions import Permission

from . import board_bp
from .services import (
    create_board,
    create_board_column,
    get_board_with_columns,
    soft_delete_board,
    view_board,
)


@board_bp.post("")
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
        "boards.get_board_route",
        room_public_id=room_public_id,
        board_public_id=board.public_id,
    )
    return resp


@board_bp.delete("/<string:board_public_id>")
@require_permission(Permission.SOFT_DELETE_BOARD)
def soft_delete_board_route(room_public_id: str, board_public_id: str):
    soft_delete_board(board_public_id)
    return (
        jsonify({"message": f"Board '{board_public_id}' has been soft deleted."}),
        200,
    )


@board_bp.get("")
@require_permission(Permission.VIEW_BOARD)
def view_board_route(room_public_id: str):
    boards = view_board(room_public_id)
    return jsonify({"boards": [board.public_id for board in boards]}), 200


@board_bp.post("/<string:board_public_id>/columns")
@require_permission(Permission.CREATE_BOARD_COLUMN)
def create_board_column_route(room_public_id: str, board_public_id: str):
    data = request.get_json(silent=True) or {}
    column = create_board_column(
        room_public_id=room_public_id,
        board_public_id=board_public_id,
        title=data.get("title"),
        wip_limit=data.get("wip_limit"),
        column_type=data.get("column_type"),
        parent_id=data.get("parent_id"),
    )
    resp = jsonify(
        {
            "board_id": board_public_id,
            "column": {
                "id": column.id,
                "title": column.title,
                "position": column.position,
                "wip_limit": column.wip_limit,
                "column_type": column.column_type,
                "parent_id": column.parent_id,
            },
        }
    )
    resp.status_code = 201
    return resp


@board_bp.get("/<string:board_public_id>")
@require_permission(Permission.VIEW_BOARD)
def get_board_route(room_public_id: str, board_public_id: str):
    board, columns = get_board_with_columns(
        room_public_id=room_public_id, board_public_id=board_public_id
    )
    return (
        jsonify(
            {
                "board": {
                    "public_id": board.public_id,
                    "name": board.name,
                    "room_id": room_public_id,
                },
                "columns": [
                    {
                        "id": column.id,
                        "title": column.title,
                        "position": column.position,
                        "wip_limit": column.wip_limit,
                        "column_type": column.column_type,
                        "parent_id": column.parent_id,
                    }
                    for column in columns
                ],
            }
        ),
        200,
    )
