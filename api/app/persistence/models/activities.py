from __future__ import annotations
from app.extensions import db
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import JSONB
from .mixins import SurrogatePK

class ActivityLog(db.Model, SurrogatePK):
    __tablename__ = "activity_logs"
    __table_args__ = (Index("ix_activity_room_created", "room_id", "created_at"),)

    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    action = db.Column(db.String(64), nullable=False)   # e.g., "card.move", "member.invite"
    payload = db.Column(JSONB)

    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)

    room = db.relationship("Room", back_populates="activity")
    actor = db.relationship("User")

    def __repr__(self) -> str:
        return f"<ActivityLog id={self.id} room={self.room_id} action={self.action}>"
