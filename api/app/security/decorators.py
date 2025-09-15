from __future__ import annotations

from functools import wraps
from typing import Callable, Optional

from app.extensions import db
from app.persistence.models import Board, BoardColumn, Card, Room, RoomMember
from app.security.roles import has_at_least
from flask import g
from sqlalchemy import and_
from werkzeug.exceptions import Forbidden, NotFound


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


def _resolve_room_id(
    kwargs, *, room_param=None, board_param=None, card_param=None, allow_deleted=False
) -> Optional[int]:
    if room_param and kwargs.get(room_param):
        return _room_id_from_room_public(
            kwargs[room_param], allow_deleted=allow_deleted
        )
    if board_param and kwargs.get(board_param):
        return _room_id_from_board_public(
            kwargs[board_param], allow_deleted=allow_deleted
        )
    if card_param and kwargs.get(card_param):
        return _room_id_from_card_public(
            kwargs[card_param], allow_deleted=allow_deleted
        )
    return None


def _lookup_membership(room_id: int, user_id: int) -> Optional[str]:
    row = (
        db.session.query(RoomMember.role)
        .filter(RoomMember.room_id == room_id, RoomMember.user_id == user_id)
        .limit(1)
        .first()
    )
    return row[0] if row else None


def require_membership(
    *,
    at_least: str = "viewer",
    room_param: Optional[str] = None,
    board_param: Optional[str] = None,
    card_param: Optional[str] = None,
    not_found_instead_of_forbidden: bool = True,
    allow_deleted: bool = False,  # <-- new: allow accessing soft-deleted resources
) -> Callable:
    def decorator(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not getattr(g, "user", None):
                raise NotFound()
            room_id = _resolve_room_id(
                kwargs,
                room_param=room_param,
                board_param=board_param,
                card_param=card_param,
                allow_deleted=allow_deleted,
            )
            if not room_id:
                raise NotFound()

            cache_key = f"_membership_{room_id}"
            role = getattr(g, cache_key, None)
            if role is None:
                role = _lookup_membership(room_id, g.user.id)
                setattr(g, cache_key, role)

            if role is None:
                if not_found_instead_of_forbidden:
                    raise NotFound()
                raise Forbidden("Not a member of this room.")

            if not has_at_least(role, at_least):
                if not_found_instead_of_forbidden:
                    raise NotFound()
                raise Forbidden(f"Requires at least '{at_least}'.")

            kwargs["_room_id"] = room_id
            kwargs["_role"] = role
            return fn(*args, **kwargs)

        return wrapper

    return decorator
