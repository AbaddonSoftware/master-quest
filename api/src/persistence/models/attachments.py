from __future__ import annotations

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, relationship
from src.extensions import db
from src.persistence.orm.mixins import DeletedAtMixin, SurrogatePK, TimestampMixin


class CardAttachment(db.Model, SurrogatePK, TimestampMixin, DeletedAtMixin):
    __tablename__ = "card_attachments"

    card_id = db.Column(
        db.Integer,
        ForeignKey("cards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind = db.Column(String(255), nullable=False)
    title = db.Column(String(255), nullable=True)
    url = db.Column(Text, nullable=True)
    path = db.Column(Text, nullable=True)
    twee = db.Column(Text, nullable=True)
    content_type = db.Column(String(255), nullable=True)
    size_bytes = db.Column(db.Integer, nullable=True)

    card: Mapped["Card"] = relationship("Card", back_populates="attachments")

    __table_args__ = (Index("ix_card_attachments_card_kind", "card_id", "kind"),)
