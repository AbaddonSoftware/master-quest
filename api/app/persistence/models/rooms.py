from __future__ import annotations

from app.extensions import db
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    Integer,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.persistence.orm.mixins import PublicIdMixin, SurrogatePK, TimestampMixin
from app.domain.security.permissions import RoomType, RoleType


class Room(db.Model, SurrogatePK, PublicIdMixin, TimestampMixin):
    __tablename__ = "rooms"

    owner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    room_type: Mapped[RoomType] = mapped_column(Enum(RoomType, name="room_type", create_constraint=True), nullable=False, server_default=RoomType.NORMAL)
    expires_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    owner: Mapped["User"] = relationship("User", back_populates="ownerships")
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
            "uq_rooms_owner_one_guest_active",
            "owner_id",
            unique=True,
            postgresql_where=text("room_type = 'GUEST'"),
        ),
        CheckConstraint(
            "(room_type <> 'GUEST') OR (expires_at IS NOT NULL)",
            name="ck_rooms_guest_requires_expires_at",
        ),
        Index(
            "ix_rooms_expiring_active",
            "expires_at",
            postgresql_where=text("room_type = 'GUEST'"),
        ),
    )


class RoomMember(db.Model, TimestampMixin):
    __tablename__ = "room_members"

    room_id: Mapped[int] = mapped_column(
        db.Integer, ForeignKey("rooms.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        db.Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role: Mapped[Enum] = db.Column(Enum(RoleType, name="role_type", create_constraint=True), nullable=False, server_default=RoleType.MEMBER)

    room: Mapped["Room"] = relationship("Room", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="memberships")

    __table_args__ = (
        UniqueConstraint("room_id", "user_id", name="uq_room_members_unique"),
        Index("ix_room_members_room_id", "room_id"),
        Index("ix_room_members_user_id", "user_id"),
    )
