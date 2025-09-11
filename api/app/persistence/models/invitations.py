from __future__ import annotations
from app.extensions import db
from sqlalchemy import UniqueConstraint, Index
from .mixins import SurrogatePK, TimestampMixin
from .enums import RoleEnum

class Invitation(db.Model, SurrogatePK, TimestampMixin):
    __tablename__ = "invitations"
    __table_args__ = (
        UniqueConstraint("token", name="uq_invitations_token"),
        Index("ix_invitations_room_expires", "room_id", "expires_at"),
    )

    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    issuer_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    role = db.Column(RoleEnum, nullable=False, server_default="member")

    token = db.Column(db.String(120), nullable=False)  # base64url/hex, >=128 bits entropy
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    used_at = db.Column(db.DateTime(timezone=True))

    room = db.relationship("Room", back_populates="invitations")
    issuer = db.relationship("User")

    def __repr__(self) -> str:
        return f"<Invitation id={self.id} room={self.room_id} expires={self.expires_at}>"
