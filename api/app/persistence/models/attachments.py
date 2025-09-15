from __future__ import annotations

from app.extensions import db
from sqlalchemy import Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from .enums import AttachmentKind
from ..orm.mixins import DeletedAtMixin, PublicIdMixin, SurrogatePK, TimestampMixin


class TweeFile(db.Model, SurrogatePK, PublicIdMixin, TimestampMixin, DeletedAtMixin):
    __tablename__ = "twee_files"
    __table_args__ = (
        Index("ix_twee_files_room", "room_id"),
        UniqueConstraint("room_id", "content_hash", name="uq_twee_room_hash"),
    )
    room_id = db.Column(
        db.Integer, db.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False
    )
    uploader_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    filename = db.Column(db.String(255), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    content_hash = db.Column(db.String(64), nullable=False)
    storage_url = db.Column(db.Text)
    blob = db.Column(db.LargeBinary)
    content = db.Column(JSONB)


class CardAttachment(db.Model, SurrogatePK, TimestampMixin, DeletedAtMixin):
    __tablename__ = "card_attachments"
    __table_args__ = (Index("ix_card_attachments_card", "card_id"),)
    card_id = db.Column(
        db.Integer, db.ForeignKey("cards.id", ondelete="CASCADE"), nullable=False
    )
    kind = db.Column(
        AttachmentKind,
        nullable=False,
        server_default="twee",
    )
    twee_file_id = db.Column(
        db.Integer, db.ForeignKey("twee_files.id", ondelete="SET NULL")
    )
    url = db.Column(db.Text)
    title = db.Column(db.String(255))
