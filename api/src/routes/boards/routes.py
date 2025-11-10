from flask import jsonify, request, url_for

from ...domain.decorators import require_permission
from ...domain.security.permissions import Permission
from . import board_bp
from .services import (
    create_board,
    create_board_column,
    get_board_with_columns,
    hard_delete_column,
    reorder_board_columns,
    reorder_column_cards,
    list_archived_items,
    restore_column,
    soft_delete_board,
    soft_delete_column,
    update_board,
    update_board_column,
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
                "cards": [],
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
                        "cards": [
                            {
                                "id": str(card.public_id),
                                "title": card.title,
                                "description": card.description,
                                "position": card.position,
                                "column_id": card.column_id,
                            }
                            for card in cards
                        ],
                    }
                    for column, cards in columns
                ],
            }
        ),
        200,
    )


@board_bp.patch("/<string:board_public_id>")
@require_permission(Permission.EDIT_BOARD)
def update_board_route(room_public_id: str, board_public_id: str):
    data = request.get_json(silent=True) or {}
    updated = update_board(
        room_public_id=room_public_id,
        board_public_id=board_public_id,
        name=data.get("name"),
    )
    return jsonify(
        {
            "board": {
                "public_id": updated.public_id,
                "name": updated.name,
            }
        }
    )


@board_bp.patch("/<string:board_public_id>/columns/<int:column_id>")
@require_permission(Permission.EDIT_BOARD_COLUMN)
def update_board_column_route(
    room_public_id: str, board_public_id: str, column_id: int
):
    data = request.get_json(silent=True) or {}
    column = update_board_column(
        room_public_id=room_public_id,
        board_public_id=board_public_id,
        column_id=column_id,
        title=data.get("title"),
        wip_limit=data.get("wip_limit"),
        wip_limit_provided="wip_limit" in data,
    )
    return jsonify(
        {
            "column": {
                "id": column.id,
                "title": column.title,
                "wip_limit": column.wip_limit,
                "position": column.position,
            }
        }
    )


@board_bp.patch("/<string:board_public_id>/columns/reorder")
@require_permission(Permission.EDIT_BOARD_COLUMN)
def reorder_board_columns_route(room_public_id: str, board_public_id: str):
    data = request.get_json(silent=True) or {}
    columns = reorder_board_columns(
        room_public_id=room_public_id,
        board_public_id=board_public_id,
        column_ids=data.get("column_ids"),
    )
    return jsonify(
        {
            "columns": [
                {
                    "id": column.id,
                    "title": column.title,
                    "position": column.position,
                }
                for column in columns
            ]
        }
    )


@board_bp.patch(
    "/<string:board_public_id>/columns/<int:column_id>/cards/reorder"
)
@require_permission(Permission.EDIT_BOARD_COLUMN)
def reorder_column_cards_route(
    room_public_id: str, board_public_id: str, column_id: int
):
    data = request.get_json(silent=True) or {}
    cards = reorder_column_cards(
        room_public_id=room_public_id,
        board_public_id=board_public_id,
        column_id=column_id,
        card_ids=data.get("card_ids"),
    )
    return jsonify(
        {
            "cards": [
                {
                    "id": str(card.public_id),
                    "column_id": card.column_id,
                    "position": card.position,
                }
                for card in cards
            ]
        }
    )


@board_bp.delete("/<string:board_public_id>/columns/<int:column_id>")
@require_permission(Permission.EDIT_BOARD_COLUMN)
def delete_board_column_route(
    room_public_id: str, board_public_id: str, column_id: int
):
    soft_delete_column(
        room_public_id=room_public_id,
        board_public_id=board_public_id,
        column_id=column_id,
    )
    return jsonify({"message": "Column archived."}), 200


@board_bp.post("/<string:board_public_id>/columns/<int:column_id>/restore")
@require_permission(Permission.EDIT_BOARD_COLUMN)
def restore_board_column_route(
    room_public_id: str, board_public_id: str, column_id: int
):
    column = restore_column(
        room_public_id=room_public_id,
        board_public_id=board_public_id,
        column_id=column_id,
    )
    return jsonify(
        {
            "column": {
                "id": column.id,
                "title": column.title,
                "wip_limit": column.wip_limit,
                "position": column.position,
            }
        }
    )


@board_bp.delete("/<string:board_public_id>/archive/columns/<int:column_id>")
@require_permission(Permission.EDIT_BOARD_COLUMN)
def hard_delete_board_column_route(
    room_public_id: str, board_public_id: str, column_id: int
):
    data = request.get_json(silent=True) or {}
    force_param = request.args.get("force", data.get("force"))
    force = False
    if isinstance(force_param, str):
        force = force_param.lower() in {"1", "true", "yes", "on"}
    elif isinstance(force_param, bool):
        force = force_param

    hard_delete_column(
        room_public_id=room_public_id,
        board_public_id=board_public_id,
        column_id=column_id,
        force=force,
    )
    return jsonify({"message": "Column permanently deleted."}), 200


@board_bp.get("/<string:board_public_id>/archive")
@require_permission(Permission.VIEW_BOARD)
def get_board_archive(room_public_id: str, board_public_id: str):
    data = list_archived_items(
        room_public_id=room_public_id, board_public_id=board_public_id
    )
    return jsonify(data), 200
