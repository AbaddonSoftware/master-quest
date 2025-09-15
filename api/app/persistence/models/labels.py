from __future__ import annotations

from app.extensions import db
from sqlalchemy import Index, UniqueConstraint

from ..orm.mixins import DeletedAtMixin, SurrogatePK, TimestampMixin


class Label(db.Model, SurrogatePK, TimestampMixin, DeletedAtMixin):
    __tablename__ = "labels"
    __table_args__ = (
        UniqueConstraint(
            "room_id", "name", name="uq_labels_room_name"
        ),  # migrate to partial unique
        Index("ix_labels_room", "room_id"),
    )
    room_id = db.Column(
        db.Integer, db.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False
    )
    name = db.Column(db.String(64), nullable=False)
    color = db.Column(db.String(16))


class CardLabel(db.Model):
    __tablename__ = "card_labels"
    __table_args__ = (
        db.UniqueConstraint("card_id", "label_id", name="uq_card_labels_card_label"),
        db.Index("ix_card_labels_label", "label_id"),
    )
    card_id = db.Column(
        db.Integer, db.ForeignKey("cards.id", ondelete="CASCADE"), primary_key=True
    )
    label_id = db.Column(
        db.Integer, db.ForeignKey("labels.id", ondelete="CASCADE"), primary_key=True
    )
