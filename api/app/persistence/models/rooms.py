from __future__ import annotations
from app.extensions import db
from sqlalchemy import UniqueConstraint, Index
from .mixins import SurrogatePK, TimestampMixin, PublicIdMixin
from .enums import RoleEnum

class Room(db.Model, SurrogatePK, PublicIdMixin, TimestampMixin):
    __tablename__ = "rooms"
    __table_args__ = (
        UniqueConstraint("owner_id", "name", name="uq_rooms_owner_name"),
        Index("ix_rooms_is_public", "is_public"),
    )

    owner_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    is_public = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))
    slug = db.Column(db.Text, nullable=True)
    __table_args__ = (
        UniqueConstraint("owner_id", "name", name="uq_rooms_owner_name"),
        Index("ix_rooms_is_public", "is_public"),
        Index("uq_rooms_owner_slug", "owner_id", "slug", unique=True, postgresql_where=db.text("slug IS NOT NULL")),
    )

    owner = db.relationship("User", foreign_keys=[owner_id])
    members = db.relationship("RoomMember", back_populates="room", cascade="all, delete-orphan")
    boards = db.relationship("Board", back_populates="room", cascade="all, delete-orphan")
    invitations = db.relationship("Invitation", back_populates="room", cascade="all, delete-orphan")
    activity = db.relationship("ActivityLog", back_populates="room", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Room id={self.id} public_id={self.public_id} name={self.name!r}>"

class RoomMember(db.Model, TimestampMixin):
    __tablename__ = "room_members"
    __table_args__ = (
        db.UniqueConstraint("room_id", "user_id", name="uq_room_members_room_user"),
        db.Index("ix_room_members_user", "user_id"),
    )

    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id", ondelete="CASCADE"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role = db.Column(RoleEnum, nullable=False)

    room = db.relationship("Room", back_populates="members")
    user = db.relationship("User")

    def __repr__(self) -> str:
        return f"<RoomMember room={self.room_id} user={self.user_id} role={self.role}>"
