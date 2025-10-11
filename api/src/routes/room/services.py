from src.domain.security.permissions import RoleType, RoomType
from src.extensions import db
from src.persistence.models import Room, RoomMember


def create_room(*, creator_user_id: int, name: str, room_type: RoomType) -> Room:
    room = Room(
        owner_id=creator_user_id,
        name=name.strip(),
        room_type=room_type,
    )
    db.session.add(room)
    db.session.flush()

    db.session.add(
        RoomMember(
            user_id=creator_user_id,
            room_id=room.id,
            role=RoleType.OWNER,
        )
    )
    db.session.commit()
    return room


def view_rooms():
    rooms = Room.query.all()
    return rooms
