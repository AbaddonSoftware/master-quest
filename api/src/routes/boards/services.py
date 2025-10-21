from enum import StrEnum

from flask import g
from sqlalchemy import func
from sqlalchemy.orm import selectinload

from ...domain.validators import validate_in_enum, validate_int, validate_str
from ...extensions import db
from ...persistence.models import Board, BoardColumn, Room

from ...domain.exceptions import ConflictError, NotFoundError


class ColumnType(StrEnum):
    STANDARD = "STANDARD"


def create_board(*, room_public_id: int, raw_name: str) -> Board:
    cleaned_name = validate_str(raw_name)
    room = db.session.execute(
        db.select(Room).where(
            Room.public_id == room_public_id, Room.deleted_at.is_(None)
        )
    ).scalar_one_or_none()
    if not room:
        raise NotFoundError("Room: '{room_public_id}' was not found.")
    exists = db.session.execute(
        db.select(func.count())
        .select_from(Board)
        .where(
            Board.room_id == room.id,
            Board.name == cleaned_name,
            Board.deleted_at.is_(None),
        )
    ).scalar_one()
    if exists:
        raise ConflictError("Board name must be unique.")  # 409

    board = Board(room_id=room.id, name=cleaned_name)
    with db.session.begin():
        db.session.add(board)
        db.session.flush()
    return board


def soft_delete_board(board_id: str):
    stmt = db.select(Board).where(
        Board.public_id == board_id, Board.deleted_at.is_(None)
    )
    board = db.session.scalar(stmt)
    if board is None:
        raise NotFoundError(f"Board '{board_id}' not found.")
    board.soft_delete(g.user.id)
    db.session.commit()


def view_board(room_public_id: str):
    stmt = (
        db.select(Board)
        .join(Room, Room.id == Board.room_id)
        .where(Board.deleted_at.is_(None), Room.public_id == room_public_id)
    )

    boards = db.session.scalars(stmt).all()
    return boards


def create_board_column(
    *,
    room_public_id: str,
    board_public_id: str,
    title: str | None,
    wip_limit: int | None = None,
    column_type: str | None = None,
    parent_id: int | None = None,
) -> BoardColumn:
    cleaned_title = validate_str(title, "title", min_len=3, max_len=64)
    limit = validate_int(
        wip_limit, "wip_limit", required=False, min_value=0, max_value=999
    )
    parent_ref = validate_int(parent_id, "parent_id", required=False, min_value=1)

    column_type_value = validate_in_enum(
        column_type or ColumnType.STANDARD.value,
        ColumnType,
        "column_type",
        required=False,
    )
    normalized_type = (
        column_type_value.lower()
        if column_type_value
        else ColumnType.STANDARD.value.lower()
    )

    board_stmt = (
        db.select(Board)
        .join(Room, Room.id == Board.room_id)
        .where(
            Board.public_id == board_public_id,
            Board.deleted_at.is_(None),
            Room.public_id == room_public_id,
        )
    )
    board = db.session.execute(board_stmt).scalar_one_or_none()
    if board is None:
        raise NotFoundError(f"Board '{board_public_id}' not found.")

    parent_column = None
    if parent_ref is not None:
        parent_column = db.session.execute(
            db.select(BoardColumn).where(
                BoardColumn.id == parent_ref,
                BoardColumn.board_id == board.id,
                BoardColumn.deleted_at.is_(None),
            )
        ).scalar_one_or_none()
        if parent_column is None:
            raise NotFoundError(
                f"Parent column '{parent_ref}' was not found on this board."
            )

    stmt = (
        db.select(func.coalesce(func.max(BoardColumn.position), -1))
        .select_from(BoardColumn)
        .where(
            BoardColumn.board_id == board.id,
            BoardColumn.deleted_at.is_(None),
        )
    )
    if parent_column is None:
        stmt = stmt.where(BoardColumn.parent_id.is_(None))
    else:
        stmt = stmt.where(BoardColumn.parent_id == parent_column.id)
    next_position = db.session.execute(stmt).scalar_one() + 1

    column = BoardColumn(
        board_id=board.id,
        parent_id=parent_column.id if parent_column else None,
        title=cleaned_title,
        position=next_position,
        wip_limit=limit,
        column_type=normalized_type,
    )
    with db.session.begin():
        db.session.add(column)
        db.session.flush()
    return column


def get_board_with_columns(
    *, room_public_id: str, board_public_id: str
) -> tuple[Board, list[BoardColumn]]:
    stmt = (
        db.select(Board)
        .options(selectinload(Board.columns))
        .join(Room, Room.id == Board.room_id)
        .where(
            Board.public_id == board_public_id,
            Board.deleted_at.is_(None),
            Room.public_id == room_public_id,
        )
    )
    board = db.session.execute(stmt).unique().scalar_one_or_none()
    if board is None:
        raise NotFoundError(f"Board '{board_public_id}' not found.")
    columns = [col for col in board.columns if not col.deleted_at]
    return board, columns
