from __future__ import annotations
from app.extensions import db
from sqlalchemy import UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB
from .mixins import SurrogatePK, TimestampMixin, PublicIdMixin
from .enums import AttachmentKind

class TweeFile(db.Model, SurrogatePK, PublicIdMixin, TimestampMixin):
    __tablename__ = "twee_files"
    __table_args__ = (
        Index("ix_twee_files_room", "room_id"),
        UniqueConstraint("room_id", "content_hash", name="uq_twee_room_hash"),
    )

    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))

    filename = db.Column(db.String(255), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    content_hash = db.Column(db.String(64), nullable=False)  # sha256 hex
    storage_url = db.Column(db.Text)                          # if using S3/MinIO
    blob = db.Column(db.LargeBinary)                          # optional inline (dev only)
    metadata = db.Column(JSONB)

    uploader = db.relationship("User")
    room = db.relationship("Room")

    def __repr__(self) -> str:
        return f"<TweeFile id={self.id} public_id={self.public_id} file={self.filename!r}>"
    
class CardAttachment(db.Model, SurrogatePK, TimestampMixin):
    __tablename__ = "card_attachments"
    __table_args__ = (Index("ix_card_attachments_card", "card_id"),)

    card_id = db.Column(db.Integer, db.ForeignKey("cards.id", ondelete="CASCADE"), nullable=False)
    kind = db.Column(AttachmentKind, nullable=False)

    twee_file_id = db.Column(db.Integer, db.ForeignKey("twee_files.id", ondelete="SET NULL"))
    url = db.Column(db.Text)                   # for kind="link" or external file
    title = db.Column(db.String(255))

    card = db.relationship("Card", back_populates="attachments")
    twee_file = db.relationship("TweeFile")

    def __repr__(self) -> str:
        return f"<CardAttachment id={self.id} card={self.card_id} kind={self.kind}>"
