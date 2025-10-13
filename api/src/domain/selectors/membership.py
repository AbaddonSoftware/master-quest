from typing import Optional

from flask import abort, g
from sqlalchemy import select
from src.domain.validators import validate_user_logged_in
from src.extensions import db
from src.persistence.models import Room, RoomMember


def get_role_in_room(room_public_id: str) -> str:
    """
    Return the role of a user in a room, or None if not a member.
    """
    user_id = validate_user_logged_in()
    subquery_room_id = (
        select(Room.id).where(Room.public_id == room_public_id).scalar_subquery()
    )
    statement = select(RoomMember.role).where(
        RoomMember.user_id == user_id,
        RoomMember.room_id == subquery_room_id,
    )
    role_in_room = db.session.execute(statement).scalar_one_or_none()
    role_in_room or abort(404)
    return role_in_room
