from __future__ import annotations
from app.extensions import db
from sqlalchemy import UniqueConstraint, Index
from .mixins import SurrogatePK, TimestampMixin

class Label(db.Model, SurrogatePK, TimestampMixin):
    __tablename__ = "labels"
    __table_args__ = (
        UniqueConstraint("room_id", "name", name="uq_labels_room_name"),
        Index("ix_labels_room", "room_id"),
    )

    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    color = db.Column(db.String(16))

    cards = db.relationship("Card", secondary="card_labels", back_populates="labels")

    def __repr__(self) -> str:
        return f"<Label id={self.id} room={self.room_id} name={self.name!r}>"

class CardLabel(db.Model):
    __tablename__ = "card_labels"
    __table_args__ = (
        db.UniqueConstraint("card_id", "label_id", name="uq_card_labels_card_label"),
        db.Index("ix_card_labels_label", "label_id"),
    )

    card_id = db.Column(db.Integer, db.ForeignKey("cards.id", ondelete="CASCADE"), primary_key=True)
    label_id = db.Column(db.Integer, db.ForeignKey("labels.id", ondelete="CASCADE"), primary_key=True)
