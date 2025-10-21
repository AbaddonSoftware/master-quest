from ...domain.security.permissions import RoleType, RoomType
from ...extensions import db
from ...persistence.models import Room, RoomMember


def create_room(
    *, creator_user_id: int, name: str, room_type: RoomType = "Normal"
) -> Room:
    room = Room(
        owner_id=creator_user_id,
        name=name.strip(),
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


def view_room(room_public_id):
    room = Room.query.filter_by(public_id=room_public_id).first()
    return room


def view_rooms():
    rooms = Room.query.all()
    return rooms
