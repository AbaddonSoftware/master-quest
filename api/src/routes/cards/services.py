from __future__ import annotations

from flask import g
from sqlalchemy import func

from ...domain.exceptions import ConflictError, NotFoundError
from ...domain.validators import (
    validate_display_text,
    validate_int,
    validate_multiline_text,
)
from ...extensions import db
from ...persistence.models import Board, BoardColumn, Card, Room


def create_card(
    *,
    room_public_id: str,
    board_public_id: str,
    column_id: int,
    title: str | None,
    description: str | None = None,
) -> Card:
    cleaned_title = validate_display_text(title, "title", min_len=1, max_len=120)
    cleaned_description = validate_multiline_text(
        description, "description", required=False, max_len=4000
    )

    column_identifier = validate_int(column_id, "column_id", required=True, min_value=1)
    assert column_identifier is not None

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

    column_stmt = (
        db.select(BoardColumn)
        .where(
            BoardColumn.id == column_identifier,
            BoardColumn.board_id == board.id,
            BoardColumn.deleted_at.is_(None),
        )
        .with_for_update()
    )
    column = db.session.execute(column_stmt).scalar_one_or_none()
    if column is None:
        raise NotFoundError(
            f"Column '{column_identifier}' was not found on this board."
        )

    _assert_wip_capacity(column)

    next_position = _next_card_position(column.id)

    card = Card(
        board_id=board.id,
        column_id=column.id,
        title=cleaned_title,
        description=cleaned_description,
        position=next_position,
    )
    db.session.add(card)
    db.session.commit()
    return card


def update_card(
    *,
    room_public_id: str,
    board_public_id: str,
    card_public_id: str,
    title: str | None = None,
    description: str | None = None,
    target_column_id: int | None = None,
) -> Card:
    card = db.session.execute(
        db.select(Card)
        .join(Board, Board.id == Card.board_id)
        .join(Room, Room.id == Board.room_id)
        .where(
            Room.public_id == room_public_id,
            Board.public_id == board_public_id,
            Card.public_id == card_public_id,
            Card.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if card is None:
        raise NotFoundError(f"Card '{card_public_id}' not found.")

    if title is not None:
        card.title = validate_display_text(title, "title", min_len=1, max_len=255)
    if description is not None:
        card.description = validate_multiline_text(
            description, "description", required=False, max_len=4000
        )

    if target_column_id is not None and target_column_id != card.column_id:
        column = db.session.execute(
            db.select(BoardColumn)
            .join(Board, Board.id == BoardColumn.board_id)
            .where(
                BoardColumn.id == target_column_id,
                BoardColumn.board_id == card.board_id,
                BoardColumn.deleted_at.is_(None),
            )
            .with_for_update()
        ).scalar_one_or_none()
        if column is None:
            raise NotFoundError(
                f"Column '{target_column_id}' was not found on this board."
            )
        _assert_wip_capacity(column, exclude_card_id=card.id)
        next_position = _next_card_position(column.id, exclude_card_id=card.id)
        card.position = next_position
        card.column_id = column.id

    db.session.commit()
    return card


def soft_delete_card(
    *, room_public_id: str, board_public_id: str, card_public_id: str
) -> None:
    card = db.session.execute(
        db.select(Card)
        .join(Board, Board.id == Card.board_id)
        .join(Room, Room.id == Board.room_id)
        .where(
            Room.public_id == room_public_id,
            Board.public_id == board_public_id,
            Card.public_id == card_public_id,
            Card.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if card is None:
        raise NotFoundError(f"Card '{card_public_id}' not found.")

    actor_id = getattr(g, "user", None).id if getattr(g, "user", None) else None
    card.soft_delete(actor_id)
    db.session.commit()


def restore_card(
    *, room_public_id: str, board_public_id: str, card_public_id: str
) -> Card:
    card = db.session.execute(
        db.select(Card)
        .join(Board, Board.id == Card.board_id)
        .join(Room, Room.id == Board.room_id)
        .where(
            Room.public_id == room_public_id,
            Board.public_id == board_public_id,
            Card.public_id == card_public_id,
            Card.deleted_at.is_not(None),
        )
    ).scalar_one_or_none()
    if card is None:
        raise NotFoundError(f"Archived card '{card_public_id}' was not found.")

    column = db.session.execute(
        db.select(BoardColumn)
        .where(BoardColumn.id == card.column_id, BoardColumn.deleted_at.is_(None))
        .with_for_update()
    ).scalar_one_or_none()
    if column is None:
        raise NotFoundError(
            "Cannot restore card because its column is archived or missing."
        )
    _assert_wip_capacity(column)

    card.restore()
    card.position = _next_card_position(column.id)
    db.session.commit()
    return card


def _next_card_position(column_id: int, *, exclude_card_id: int | None = None) -> int:
    stmt = (
        db.select(Card.position)
        .where(Card.column_id == column_id, Card.deleted_at.is_(None))
        .order_by(Card.position.desc())
        .limit(1)
        .with_for_update()
    )
    if exclude_card_id is not None:
        stmt = stmt.where(Card.id != exclude_card_id)
    highest = db.session.execute(stmt).scalar_one_or_none()
    return (highest or -1) + 1


def _assert_wip_capacity(
    column: BoardColumn, *, exclude_card_id: int | None = None
) -> None:
    if column.wip_limit is None:
        return
    stmt = (
        db.select(func.count())
        .select_from(Card)
        .where(Card.column_id == column.id, Card.deleted_at.is_(None))
    )
    if exclude_card_id is not None:
        stmt = stmt.where(Card.id != exclude_card_id)
    current = db.session.execute(stmt).scalar_one()
    if current >= column.wip_limit:
        raise ConflictError(
            f"WIP limit reached for column '{column.title}'. Move or complete an existing card first."
        )
