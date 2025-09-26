from __future__ import annotations

from app.extensions import db
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, relationship

from ..orm.mixins import PublicIdMixin, SurrogatePK, TimestampMixin
from .enums import Role, RoomKind


class Room(db.Model, SurrogatePK, PublicIdMixin, TimestampMixin):
    __tablename__ = "rooms"

    owner_id = db.Column(
        db.Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name = db.Column(String(128), nullable=False)
    is_public = db.Column(Boolean, nullable=False, server_default=text("false"))
    kind = db.Column(RoomKind, nullable=False, server_default=text("'normal'"))
    expires_at = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    owner: Mapped["User"] = relationship("User", back_populates="rooms_owned")
    members: Mapped[list["RoomMember"]] = relationship(
        "RoomMember",
        back_populates="room",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    boards: Mapped[list["Board"]] = relationship(
        "Board",
        back_populates="room",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        UniqueConstraint("owner_id", "name", name="uq_rooms_owner_name"),
        Index(
            "uq_rooms_owner_one_guest_active",  # name
            "owner_id",  # column(s)
            unique=True,
            postgresql_where=text("kind = 'guest'"),
        ),
        Index("ix_rooms_is_public", "is_public"),
        CheckConstraint(
            "(kind <> 'guest') OR (expires_at IS NOT NULL)",
            name="ck_rooms_guest_requires_expires_at",
        ),
        Index(
            "ix_rooms_expiring_active",
            "expires_at",
            postgresql_where=text("kind = 'guest'"),
        ),
    )


class RoomMember(db.Model):
    __tablename__ = "room_members"

    room_id = db.Column(
        db.Integer, ForeignKey("rooms.id", ondelete="CASCADE"), primary_key=True
    )
    user_id = db.Column(
        db.Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role = db.Column(Role, nullable=False, server_default=text("'member'"))
    joined_at = db.Column(
        db.DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    room: Mapped["Room"] = relationship("Room", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="memberships")

    __table_args__ = (
        UniqueConstraint("room_id", "user_id", name="uq_room_members_unique"),
        Index("ix_room_members_room_id", "room_id"),
        Index("ix_room_members_user_id", "user_id"),
    )
