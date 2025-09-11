from __future__ import annotations
from app.extensions import db
from sqlalchemy import Index
from .mixins import SurrogatePK, TimestampMixin

class CardComment(db.Model):
    __tablename__ = "card_comments"
    __table_args__ = (
        Index("ix_card_comments_card_created", "card_id", "created_at"),
        Index("ix_card_comments_card_updated", "card_id", "updated_at"),
    )

    id = db.Column(db.Integer, primary_key=True)

    card_id = db.Column(db.Integer, db.ForeignKey("cards.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))

    body = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())
    edited_by_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    edit_count = db.Column(db.Integer, nullable=False, server_default="0")

    card = db.relationship("Card", back_populates="comments")
    author = db.relationship("User", foreign_keys=[author_id])
    edited_by = db.relationship("User", foreign_keys=[edited_by_id])

    edits = db.relationship(
        "CommentEdit",
        back_populates="comment",
        cascade="all, delete-orphan",
        order_by="CommentEdit.created_at.desc()",
    )

    def __repr__(self) -> str:
        return f"<CardComment id={self.id} card={self.card_id} edits={self.edit_count}>"

class CommentEdit(db.Model):
    __tablename__ = "comment_edits"
    __table_args__ = (
        Index("ix_comment_edits_comment_created", "comment_id", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey("card_comments.id", ondelete="CASCADE"), nullable=False, index=True)
    editor_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), index=True)

    previous_body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)

    comment = db.relationship("CardComment", back_populates="edits")
    editor = db.relationship("User")

    def __repr__(self) -> str:
        return f"<CommentEdit id={self.id} comment={self.comment_id}>"
