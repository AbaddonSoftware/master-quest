from flask import abort, g, request
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from ...domain.validators import validate_in_enum, validate_int, validate_str
from ...extensions import db
from ...persistence.models import Board, Room

from ...domain.exceptions import ConflictError, NotFoundError


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
    board_public_id: str, title: str, wip_limit: int, column_type: str
):
    pass
