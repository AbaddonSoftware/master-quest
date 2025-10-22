from sqlalchemy import select

from ...extensions import db
from ...persistence.models import Room, RoomMember
from ..exceptions import ForbiddenError
from ..validators import validate_user_logged_in


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
    if not role_in_room:
        raise ForbiddenError()
    return role_in_room
