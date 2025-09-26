from __future__ import annotations

from functools import wraps
from typing import Callable, Optional

from app.extensions import db
from app.persistence.models import Board, BoardColumn, Card, Room, RoomMember
from flask import g
from sqlalchemy import and_
from werkzeug.exceptions import Forbidden, NotFound

from .permissions import Permission
from .policy import can

# --- Room resolvers ---


def _room_id_from_room_public(room_public_id, *, allow_deleted=False) -> Optional[int]:
    q = db.session.query(Room.id).filter(Room.public_id == room_public_id)
    if not allow_deleted:
        q = q.filter(Room.deleted_at.is_(None))
    row = q.first()
    return row[0] if row else None


def _room_id_from_board_public(
    board_public_id, *, allow_deleted=False
) -> Optional[int]:
    q = db.session.query(Board.room_id).filter(Board.public_id == board_public_id)
    if not allow_deleted:
        q = q.filter(Board.deleted_at.is_(None))
    row = q.first()
    return row[0] if row else None


def _room_id_from_card_public(card_public_id, *, allow_deleted=False) -> Optional[int]:
    q = (
        db.session.query(Room.id)
        .join(Board, Board.room_id == Room.id)
        .join(BoardColumn, BoardColumn.board_id == Board.id)
        .join(Card, Card.column_id == BoardColumn.id)
        .filter(Card.public_id == card_public_id)
    )
    if not allow_deleted:
        q = q.filter(
            and_(
                Room.deleted_at.is_(None),
                Board.deleted_at.is_(None),
                BoardColumn.deleted_at.is_(None),
                Card.deleted_at.is_(None),
            )
        )
    row = q.first()
    return row[0] if row else None


def _room_id_from_comment_public(
    comment_public_id, *, allow_deleted=False
) -> Optional[int]:
    from app.persistence.models import Comment

    q = (
        db.session.query(Room.id)
        .join(Board, Board.room_id == Room.id)
        .join(BoardColumn, BoardColumn.board_id == Board.id)
        .join(Card, Card.column_id == BoardColumn.id)
        .join(Comment, Comment.card_id == Card.id)
        .filter(Comment.public_id == comment_public_id)
    )
    if not allow_deleted:
        q = q.filter(
            and_(
                Room.deleted_at.is_(None),
                Board.deleted_at.is_(None),
                BoardColumn.deleted_at.is_(None),
                Card.deleted_at.is_(None),
                Comment.deleted_at.is_(None),
            )
        )
    row = q.first()
    return row[0] if row else None


# --- Membership / ownership / authorship ---


def _lookup_membership(room_id: int, user_id: int) -> Optional[str]:
    row = (
        db.session.query(RoomMember.role)
        .filter(RoomMember.room_id == room_id, RoomMember.user_id == user_id)
        .limit(1)
        .first()
    )
    return row[0] if row else None


def _is_room_owner(room_id: int, user_id: int) -> bool:
    row = db.session.query(Room.owner_id).filter(Room.id == room_id).first()
    return bool(row and row[0] == user_id)


def _is_comment_author(comment_public_id, user_id: int, *, allow_deleted=False) -> bool:
    from app.persistence.models import Comment

    q = (
        db.session.query(Comment.author_id)
        .filter(Comment.public_id == comment_public_id)
        .join(Card, Card.id == Comment.card_id)
        .join(BoardColumn, BoardColumn.id == Card.column_id)
        .join(Board, Board.id == BoardColumn.board_id)
        .join(Room, Room.id == Board.room_id)
    )
    if not allow_deleted:
        q = q.filter(
            Room.deleted_at.is_(None),
            Board.deleted_at.is_(None),
            BoardColumn.deleted_at.is_(None),
            Card.deleted_at.is_(None),
            Comment.deleted_at.is_(None),
        )
    row = q.first()
    return bool(row and row[0] == user_id)


def _is_card_author(card_public_id, user_id: int, *, allow_deleted=False) -> bool:
    q = (
        db.session.query(Card.author_id)
        .filter(Card.public_id == card_public_id)
        .join(BoardColumn, BoardColumn.id == Card.column_id)
        .join(Board, Board.id == BoardColumn.board_id)
        .join(Room, Room.id == Board.room_id)
    )
    if not allow_deleted:
        q = q.filter(
            Room.deleted_at.is_(None),
            Board.deleted_at.is_(None),
            BoardColumn.deleted_at.is_(None),
            Card.deleted_at.is_(None),
        )
    row = q.first()
    return bool(row and row[0] == user_id)


# --- permission decorator ---


def require_permission(
    *,
    permission: Permission,
    room_param: Optional[str] = None,  # e.g. "room_public_id"
    board_param: Optional[str] = None,  # e.g. "board_public_id"
    card_param: Optional[str] = None,  # e.g. "card_public_id"
    comment_param: Optional[str] = None,  # e.g. "comment_public_id"
    not_found_instead_of_forbidden: bool = True,
    allow_deleted: bool = False,
):

    # Derive room_id, membership, and flags (is_owner/is_author) from the database.

    def decorator(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not getattr(g, "user", None):
                raise NotFound()

            # Resolve room_id
            room_id = None
            if room_param and kwargs.get(room_param):
                room_id = _room_id_from_room_public(
                    kwargs[room_param], allow_deleted=allow_deleted
                )
            elif board_param and kwargs.get(board_param):
                room_id = _room_id_from_board_public(
                    kwargs[board_param], allow_deleted=allow_deleted
                )
            elif card_param and kwargs.get(card_param):
                room_id = _room_id_from_card_public(
                    kwargs[card_param], allow_deleted=allow_deleted
                )
            elif comment_param and kwargs.get(comment_param):
                room_id = _room_id_from_comment_public(
                    kwargs[comment_param], allow_deleted=allow_deleted
                )

            if room_id is None:
                raise NotFound()

            # Membership
            cache_key = f"_membership_{room_id}"
            role = getattr(g, cache_key, None)
            if role is None:
                role = _lookup_membership(room_id, g.user.id)
                setattr(g, cache_key, role)

            if role is None:
                raise (
                    NotFound()
                    if not_found_instead_of_forbidden
                    else Forbidden("Not a member of this room.")
                )

            # Flags
            is_owner = _is_room_owner(room_id, g.user.id)
            is_author = False
            if card_param and kwargs.get(card_param):
                is_author = _is_card_author(
                    kwargs[card_param], g.user.id, allow_deleted=allow_deleted
                )
            elif comment_param and kwargs.get(comment_param):
                is_author = _is_comment_author(
                    kwargs[comment_param], g.user.id, allow_deleted=allow_deleted
                )

            ctx = {"is_owner": is_owner, "is_author": is_author}

            # Policy check
            if not can(role=role, permission=permission, ctx=ctx):
                raise (
                    NotFound()
                    if not_found_instead_of_forbidden
                    else Forbidden("Insufficient privileges.")
                )

            # # Stash trusted context
            # kwargs["_room_id"] = room_id
            # kwargs["_role"] = role
            # kwargs["_ctx"] = ctx

            g.auth = type("AuthCtx", (), {})()
            g.auth.room_id = room_id
            g.auth.role = role
            g.auth.ctx = ctx

            return fn(*args, **kwargs)

        return wrapper

    return decorator
