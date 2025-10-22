from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from flask import g
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ...domain.exceptions import ForbiddenError, NotFoundError, ValidationError
from ...domain.security.permissions import RoleType, RoomType
from ...domain.validators import validate_display_text, validate_in_enum, validate_int
from ...extensions import db
from ...persistence.models import (
    Board,
    BoardColumn,
    Card,
    Invite,
    InviteRedemption,
    Room,
    RoomMember,
    User,
)

DEFAULT_BOARD_NAME = "Adventure Roadmap"
DEFAULT_INVITE_VALID_FOR_HOURS = 24 * 7
ALLOWED_INVITE_ROLES = {RoleType.VIEWER, RoleType.MEMBER}

ROLE_PRIORITY: dict[RoleType, int] = {
    RoleType.VIEWER: 1,
    RoleType.MEMBER: 2,
    RoleType.ADMIN: 3,
    RoleType.OWNER: 4,
}


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
    stmt = (
        select(Room)
        .options(
            selectinload(Room.boards),
            selectinload(Room.members).selectinload(RoomMember.user),
        )
        .where(Room.public_id == room_public_id)
    )
    return db.session.execute(stmt).scalars().unique().one_or_none()


def view_rooms(user_id: int) -> list[Room]:
    stmt = (
        select(Room)
        .join(RoomMember, RoomMember.room_id == Room.id)
        .options(
            selectinload(Room.boards),
            selectinload(Room.members).selectinload(RoomMember.user),
        )
        .where(RoomMember.user_id == user_id)
    )
    rooms = db.session.execute(stmt).scalars().unique().all()
    return rooms


def leave_room(*, room_public_id: str, user_id: int) -> None:
    room = _get_room_by_public_id(room_public_id)
    membership = db.session.execute(
        select(RoomMember).where(
            RoomMember.room_id == room.id,
            RoomMember.user_id == user_id,
        )
    ).scalar_one_or_none()
    if membership is None:
        raise ForbiddenError("You are not a member of this room.")
    if room.owner_id == user_id:
        raise ForbiddenError("Room owners cannot leave their own room.")
    db.session.delete(membership)
    db.session.commit()


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


def _get_room_by_public_id(room_public_id: str) -> Room:
    room = db.session.execute(
        select(Room).where(Room.public_id == room_public_id)
    ).scalar_one_or_none()
    if room is None:
        raise NotFoundError(f"Room '{room_public_id}' not found.")
    return room


def _generate_invite_code() -> str:
    for _ in range(10):
        candidate = secrets.token_urlsafe(8)
        exists = db.session.execute(
            select(Invite.id).where(Invite.code == candidate)
        ).scalar_one_or_none()
        if not exists:
            return candidate
    raise ValidationError("Unable to generate a unique invite code. Please try again.")


def _normalize_name(value: str | None) -> str:
    return " ".join((value or "").split()).strip()


def list_room_members(room_public_id: str) -> list[tuple[RoomMember, User]]:
    stmt = (
        select(RoomMember, User)
        .join(Room, Room.id == RoomMember.room_id)
        .join(User, User.id == RoomMember.user_id)
        .where(Room.public_id == room_public_id)
        .order_by(User.display_name.is_(None), User.display_name, User.name)
    )
    rows = db.session.execute(stmt).all()
    return rows


def update_room_member_role(
    *,
    room_public_id: str,
    member_public_id: str,
    role: str | None,
    confirmation_name: str | None,
) -> tuple[RoomMember, User]:
    desired_role_value = validate_in_enum(role, RoleType, "role")
    desired_role = RoleType(desired_role_value)
    if desired_role == RoleType.OWNER:
        raise ValidationError("Owner role cannot be assigned manually.")

    stmt = (
        select(RoomMember, User, Room)
        .join(Room, Room.id == RoomMember.room_id)
        .join(User, User.id == RoomMember.user_id)
        .where(Room.public_id == room_public_id, User.public_id == member_public_id)
    )
    record = db.session.execute(stmt).first()
    if not record:
        raise NotFoundError("Member not found in this room.")
    member, user, room = record

    if member.role == RoleType.OWNER:
        raise ForbiddenError("Room owners cannot be demoted.")

    current_priority = ROLE_PRIORITY.get(member.role, 0)
    desired_priority = ROLE_PRIORITY.get(desired_role, 0)

    if desired_priority > current_priority:
        expected_name = _normalize_name(user.display_name or user.name)
        provided = validate_display_text(
            confirmation_name,
            "confirmation_name",
            required=True,
            min_len=1,
            max_len=128,
        )
        if not expected_name:
            raise ValidationError("Unable to confirm promotion: member name missing.")
        if _normalize_name(provided).casefold() != expected_name.casefold():
            raise ValidationError(
                "Type the member's name exactly to confirm promoting them."
            )

    if desired_role == member.role:
        return member, user

    member.role = desired_role
    db.session.commit()
    return member, user


def list_room_invites(room_public_id: str) -> list[Invite]:
    stmt = (
        select(Invite)
        .options(selectinload(Invite.redemptions))
        .join(Room, Room.id == Invite.room_id)
        .where(Invite.deleted_at.is_(None), Room.public_id == room_public_id)
        .order_by(Invite.created_at.desc())
    )
    invites = db.session.execute(stmt).scalars().unique().all()
    return invites


def create_room_invite(
    *,
    room_public_id: str,
    role: str | None,
    max_uses: int | None,
    expires_in_hours: int | None,
    creator_user_id: int,
) -> Invite:
    normalized_role_value = validate_in_enum(role, RoleType, "role")
    invite_role = RoleType(normalized_role_value)
    if invite_role not in ALLOWED_INVITE_ROLES:
        allowed = ", ".join(sorted(r.value for r in ALLOWED_INVITE_ROLES))
        raise ValidationError(f"Invites may only assign one of: {allowed}.")

    uses = validate_int(
        max_uses,
        "max_uses",
        required=False,
        min_value=1,
        max_value=50,
    )
    expiry_hours = validate_int(
        expires_in_hours,
        "expires_in_hours",
        required=False,
        min_value=1,
        max_value=24 * 30,
    )
    room = _get_room_by_public_id(room_public_id)

    expires_at = None
    if expiry_hours is None:
        expires_at = datetime.now(timezone.utc) + timedelta(
            hours=DEFAULT_INVITE_VALID_FOR_HOURS
        )
    else:
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expiry_hours)

    invite = Invite(
        room_id=room.id,
        created_by_id=creator_user_id,
        code=_generate_invite_code(),
        role=invite_role,
        redemption_max=uses or 1,
        expires_at=expires_at,
    )
    db.session.add(invite)
    db.session.commit()
    return invite


def revoke_room_invite(
    *, room_public_id: str, invite_code: str, actor_user_id: int
) -> Invite:
    cleaned_code = (invite_code or "").strip()
    if not cleaned_code:
        raise ValidationError("Invite code is required.")
    stmt = (
        select(Invite)
        .join(Room, Room.id == Invite.room_id)
        .where(
            Invite.code == cleaned_code,
            Invite.deleted_at.is_(None),
            Room.public_id == room_public_id,
        )
    )
    invite = db.session.execute(stmt).scalar_one_or_none()
    if invite is None:
        raise NotFoundError("Invite not found.")
    invite.soft_delete(actor_id=actor_user_id)
    db.session.commit()
    return invite


def accept_invite_code(*, code: str, user_id: int) -> tuple[RoomMember, Invite, Room]:
    cleaned_code = (code or "").strip()
    if not cleaned_code:
        raise ValidationError("Invite code is required.")
    stmt = (
        select(Invite, Room)
        .options(selectinload(Invite.redemptions))
        .join(Room, Room.id == Invite.room_id)
        .where(Invite.code == cleaned_code, Invite.deleted_at.is_(None))
    )
    record = db.session.execute(stmt).first()
    if record is None:
        raise NotFoundError("Invite code not recognised.")
    invite, room = record

    if invite.expires_at and invite.expires_at < datetime.now(timezone.utc):
        raise ValidationError("This invite has expired.")

    redemption_count = len(invite.redemptions)
    if redemption_count >= invite.redemption_max:
        raise ForbiddenError(
            "This invite has already been used the maximum number of times."
        )

    existing_membership = db.session.execute(
        select(RoomMember).where(
            RoomMember.room_id == invite.room_id, RoomMember.user_id == user_id
        )
    ).scalar_one_or_none()

    if existing_membership is None:
        membership = RoomMember(
            room_id=invite.room_id,
            user_id=user_id,
            role=invite.role,
        )
        db.session.add(membership)
    else:
        membership = existing_membership
        current_priority = ROLE_PRIORITY.get(membership.role, 0)
        invite_priority = ROLE_PRIORITY.get(invite.role, 0)
        if invite_priority > current_priority:
            membership.role = invite.role

    already_redeemed = any(
        redemption.redeemed_by_id == user_id for redemption in invite.redemptions
    )
    if not already_redeemed:
        redemption = InviteRedemption(
            invite_id=invite.id,
            redeemed_by_id=user_id,
        )
        db.session.add(redemption)

    db.session.commit()
    return membership, invite, room
