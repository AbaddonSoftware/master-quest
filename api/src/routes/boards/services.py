from enum import StrEnum

from flask import g
from sqlalchemy import func
from sqlalchemy.orm import selectinload

from ...domain.exceptions import ConflictError, NotFoundError
from ...domain.validators import validate_display_text, validate_in_enum, validate_int
from ...extensions import db
from ...persistence.models import Board, BoardColumn, Card, Room


class ColumnType(StrEnum):
    STANDARD = "STANDARD"


def create_board(*, room_public_id: int, raw_name: str) -> Board:
    cleaned_name = validate_display_text(raw_name, "name", min_len=3, max_len=64)
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
    cleaned_title = validate_display_text(title, "title", min_len=3, max_len=64)
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

    position_query = (
        db.select(func.coalesce(func.max(BoardColumn.position), -1))
        .select_from(BoardColumn)
        .where(
            BoardColumn.board_id == board.id,
            BoardColumn.deleted_at.is_(None),
        )
    )
    if parent_column is None:
        position_query = position_query.where(BoardColumn.parent_id.is_(None))
    else:
        position_query = position_query.where(BoardColumn.parent_id == parent_column.id)
    next_position = db.session.execute(position_query).scalar_one() + 1

    column = BoardColumn(
        board_id=board.id,
        parent_id=parent_column.id if parent_column else None,
        title=cleaned_title,
        position=next_position,
        wip_limit=limit,
        column_type=normalized_type,
    )
    db.session.add(column)
    db.session.commit()
    return column


def get_board_with_columns(
    *, room_public_id: str, board_public_id: str
) -> tuple[Board, list[tuple[BoardColumn, list[Card]]]]:
    stmt = (
        db.select(Board)
        .options(
            selectinload(Board.columns).selectinload(BoardColumn.cards),
        )
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

    column_payload: list[tuple[BoardColumn, list[Card]]] = []
    for column in sorted(board.columns, key=lambda c: c.position):
        if column.deleted_at:
            continue
        active_cards = sorted(
            (card for card in column.cards if not card.deleted_at),
            key=lambda c: c.position,
        )
        column_payload.append((column, active_cards))
    return board, column_payload


def update_board(
    *, room_public_id: str, board_public_id: str, name: str | None
) -> Board:
    cleaned_name = validate_display_text(name, "name", min_len=3, max_len=64)
    board = db.session.execute(
        db.select(Board)
        .join(Room, Room.id == Board.room_id)
        .where(
            Room.public_id == room_public_id,
            Board.public_id == board_public_id,
            Board.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if board is None:
        raise NotFoundError(f"Board '{board_public_id}' not found.")

    board.name = cleaned_name
    db.session.commit()
    return board


def update_board_column(
    *,
    room_public_id: str,
    board_public_id: str,
    column_id: int,
    title: str | None = None,
    wip_limit: int | None = None,
    wip_limit_provided: bool = False,
) -> BoardColumn:
    cleaned_title = (
        validate_display_text(title, "title", min_len=3, max_len=64)
        if title is not None
        else None
    )
    limit = (
        validate_int(wip_limit, "wip_limit", required=False, min_value=0, max_value=999)
        if wip_limit_provided
        else None
    )

    column = db.session.execute(
        db.select(BoardColumn)
        .join(Board, Board.id == BoardColumn.board_id)
        .join(Room, Room.id == Board.room_id)
        .where(
            Room.public_id == room_public_id,
            Board.public_id == board_public_id,
            BoardColumn.id == column_id,
            BoardColumn.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if column is None:
        raise NotFoundError(f"Column '{column_id}' not found on this board.")

    if cleaned_title is not None:
        column.title = cleaned_title
    if wip_limit_provided:
        column.wip_limit = limit

    db.session.commit()
    return column


def soft_delete_column(
    *, room_public_id: str, board_public_id: str, column_id: int
) -> None:
    column = db.session.execute(
        db.select(BoardColumn)
        .join(Board, Board.id == BoardColumn.board_id)
        .join(Room, Room.id == Board.room_id)
        .where(
            Room.public_id == room_public_id,
            Board.public_id == board_public_id,
            BoardColumn.id == column_id,
            BoardColumn.deleted_at.is_(None),
        )
        .options(selectinload(BoardColumn.cards))
    ).scalar_one_or_none()
    if column is None:
        raise NotFoundError(f"Column '{column_id}' not found on this board.")

    column.soft_delete(
        getattr(g, "user", None).id if getattr(g, "user", None) else None
    )
    for card in column.cards:
        card.soft_delete(
            getattr(g, "user", None).id if getattr(g, "user", None) else None
        )
    db.session.commit()


def restore_column(
    *, room_public_id: str, board_public_id: str, column_id: int
) -> BoardColumn:
    column = db.session.execute(
        db.select(BoardColumn)
        .join(Board, Board.id == BoardColumn.board_id)
        .join(Room, Room.id == Board.room_id)
        .where(
            Room.public_id == room_public_id,
            Board.public_id == board_public_id,
            BoardColumn.id == column_id,
            BoardColumn.deleted_at.is_not(None),
        )
        .options(selectinload(BoardColumn.cards))
    ).scalar_one_or_none()
    if column is None:
        raise NotFoundError(f"Archived column '{column_id}' was not found.")

    column.restore()
    for card in column.cards:
        card.restore()

    db.session.commit()
    return column


def list_archived_items(
    *, room_public_id: str, board_public_id: str
) -> dict[str, list]:
    board = db.session.execute(
        db.select(Board)
        .join(Room, Room.id == Board.room_id)
        .where(
            Room.public_id == room_public_id,
            Board.public_id == board_public_id,
            Board.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if board is None:
        raise NotFoundError(f"Board '{board_public_id}' not found.")

    archived_columns = (
        db.session.execute(
            db.select(BoardColumn)
            .where(
                BoardColumn.board_id == board.id,
                BoardColumn.deleted_at.is_not(None),
            )
            .order_by(BoardColumn.deleted_at.desc())
        )
        .scalars()
        .all()
    )

    archived_cards = (
        db.session.execute(
            db.select(Card)
            .where(
                Card.board_id == board.id,
                Card.deleted_at.is_not(None),
            )
            .order_by(Card.deleted_at.desc())
        )
        .scalars()
        .all()
    )

    return {
        "columns": [
            {
                "id": column.id,
                "title": column.title,
                "deleted_at": (
                    column.deleted_at.isoformat() if column.deleted_at else None
                ),
            }
            for column in archived_columns
        ],
        "cards": [
            {
                "public_id": str(card.public_id),
                "title": card.title,
                "column_id": card.column_id,
                "deleted_at": card.deleted_at.isoformat() if card.deleted_at else None,
            }
            for card in archived_cards
        ],
    }
