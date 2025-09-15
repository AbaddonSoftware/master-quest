from __future__ import annotations

from app.extensions import db
from sqlalchemy import Index, UniqueConstraint, and_
from sqlalchemy.orm import foreign

from .enums import Role
from ..orm.mixins import DeletedAtMixin, PublicIdMixin, SurrogatePK, TimestampMixin


class Room(db.Model, SurrogatePK, PublicIdMixin, TimestampMixin, DeletedAtMixin):
    __tablename__ = "rooms"
    __table_args__ = (
        UniqueConstraint(
            "owner_id", "name", name="uq_rooms_owner_name"
        ),  # replace with partial unique via Alembic
        Index("ix_rooms_is_public", "is_public"),
        Index(
            "uq_rooms_owner_slug",
            "owner_id",
            "slug",
            unique=True,
            postgresql_where=db.text("slug IS NOT NULL AND deleted_at IS NULL"),
        ),
    )
    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name = db.Column(db.String(120), nullable=False)
    is_public = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))
    slug = db.Column(db.Text)

    owner = db.relationship("User", foreign_keys=[owner_id])

    # IMPORTANT: remove delete-orphan; we soft-delete children via service code when needed.
    boards = db.relationship(
        "Board",
        primaryjoin="and_(Room.id == foreign(Board.room_id), Board.deleted_at.is_(None))",
        lazy="selectin",
    )
    invitations = db.relationship(
        "Invitation", back_populates="room", cascade="all, delete-orphan"
    )
    activity = db.relationship(
        "ActivityLog", back_populates="room", cascade="all, delete-orphan"
    )


class RoomMember(db.Model, TimestampMixin):
    __tablename__ = "room_members"
    __table_args__ = (db.Index("ix_room_members_user", "user_id"),)
    room_id = db.Column(
        db.Integer, db.ForeignKey("rooms.id", ondelete="CASCADE"), primary_key=True
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role = db.Column(
        Role,
        nullable=False,
        server_default="viewer",
    )

    room = db.relationship("Room")
    user = db.relationship("User")
