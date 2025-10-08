from uuid import uuid4
from app.extensions import db
from app.persistence.models import Room, RoomMember
from app.domain.security.permissions import RoleType, RoomType

def create_room(*, creator_user_id: int, name: str, room_type: RoomType) -> Room:
    room = Room(
        owner_id=creator_user_id,
        public_id=str(uuid4()),
        name=name.strip(),
        room_type=room_type,
    )
    db.session.add(room)
    db.session.flush()

    db.session.add(RoomMember(
        user_id=creator_user_id,
        room_id=room.id,
        role=RoleType.OWNER,
    ))
    db.session.commit()
    return room