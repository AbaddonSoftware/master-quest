from sqlalchemy import select

from ...domain.exceptions import ForbiddenError, NotFoundError
from ...domain.security.permissions import RoleType, RoomType
from ...extensions import db
from ...persistence.models import Board, BoardColumn, Card, Room, RoomMember


DEFAULT_BOARD_NAME = "Adventure Roadmap"

def _seed_default_board(room: Room) -> None:
    board = Board(room_id=room.id, name=DEFAULT_BOARD_NAME)
    db.session.add(board)
    db.session.flush()

    column_specs = [
        {
            "title": "Quest Backlog · Incoming Ideas",
            "wip_limit": 6,
            "cards": [
                (
                    "Capture Guild Requests",
                    "List ideas, bug reports, or enhancements as soon as they appear so the guild never forgets them.",
                ),
                (
                    "Prioritize This Week's Adventures",
                    "Choose which quests move forward next and drag them into Active Quests when you're ready to work.",
                ),
            ],
        },
        {
            "title": "Active Quests · In Progress",
            "wip_limit": 4,
            "cards": [
                (
                    "Craft the Perfect Story Card",
                    "Use the description to explain the why, who, and victory condition for the quest you're tackling.",
                ),
                (
                    "Co-op Sync",
                    "Leave notes or links teammates will need while you collaborate on this adventure.",
                ),
            ],
        },
        {
            "title": "Hall of Legends · Completed",
            "wip_limit": None,
            "cards": [
                (
                    "Celebrate a Win",
                    "Move quests here when you finish them and jot down what went well so future heroes learn from it.",
                )
            ],
        },
    ]

    for column_index, spec in enumerate(column_specs):
        column = BoardColumn(
            board_id=board.id,
            title=spec["title"],
            position=column_index,
            wip_limit=spec["wip_limit"],
            column_type="standard",
        )
        db.session.add(column)
        db.session.flush()

        for card_index, (title, description) in enumerate(spec["cards"]):
            db.session.add(
                Card(
                    board_id=board.id,
                    column_id=column.id,
                    title=title,
                    description=description,
                    position=card_index,
                )
            )


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
    _seed_default_board(room)
    db.session.commit()
    return room


def view_room(room_public_id: str) -> Room | None:
    return Room.query.filter_by(public_id=room_public_id).first()


def view_rooms(user_id: int) -> list[Room]:
    stmt = (
        select(Room)
        .join(RoomMember, RoomMember.room_id == Room.id)
        .where(RoomMember.user_id == user_id)
    )
    rooms = db.session.execute(stmt).scalars().unique().all()
    return rooms


def delete_room(*, room_public_id: str, actor_user_id: int) -> None:
    room = db.session.execute(
        select(Room).where(Room.public_id == room_public_id)
    ).scalar_one_or_none()
    if room is None:
        raise NotFoundError(f"Room '{room_public_id}' not found.")
    if room.owner_id != actor_user_id:
        raise ForbiddenError("Only the room owner can delete this room.")
    db.session.delete(room)
    db.session.commit()
