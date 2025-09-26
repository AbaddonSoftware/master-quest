from __future__ import annotations

from app.extensions import db
from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, relationship

from ..orm.mixins import DeletedAtMixin, SurrogatePK, TimestampMixin


class Invitation(db.Model, SurrogatePK, TimestampMixin, DeletedAtMixin):
    __tablename__ = "invitations"

    room_id = db.Column(
        db.Integer,
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_by_id = db.Column(
        db.Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    code_hash = db.Column(String(128), nullable=False)  # HMAC-SHA256 hex
    redemption_max = db.Column(db.Integer, nullable=False)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)

    room: Mapped["Room"] = relationship("Room")
    creator: Mapped["User"] = relationship("User")

    __table_args__ = (
        CheckConstraint("redemption_max >= 1", name="ck_invites_redemption_max"),
        Index(
            "uq_invites_room_code_hash_active",
            "room_id",
            "code_hash",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index("ix_invites_room_codehash", "room_id", "code_hash"),
        Index("ix_invites_expires_at", "expires_at"),
    )


class InviteRedemption(db.Model, SurrogatePK, TimestampMixin):
    __tablename__ = "invite_redemptions"

    invite_id = db.Column(
        db.Integer,
        ForeignKey("invitations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    redeemed_by_id = db.Column(
        db.Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )
    redeemed_at = db.Column(
        db.DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    invite: Mapped["Invitation"] = relationship("Invitation")
    redeemed_by: Mapped["User"] = relationship("User")

    __table_args__ = (
        UniqueConstraint(
            "invite_id", "redeemed_by_id", name="uq_redemptions_invite_user"
        ),
        Index("ix_redemptions_invite", "invite_id"),
    )
