from __future__ import annotations

from app.extensions import db
from sqlalchemy import CheckConstraint, ForeignKey, Index, Text, text
from sqlalchemy.orm import Mapped, backref, relationship

from ..orm.mixins import DeletedAtMixin, SurrogatePK, TimestampMixin


class Comment(db.Model, SurrogatePK, TimestampMixin, DeletedAtMixin):
    __tablename__ = "comments"

    card_id = db.Column(
        db.Integer,
        ForeignKey("cards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_id = db.Column(
        db.Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    parent_id = db.Column(
        db.Integer, ForeignKey("comments.id", ondelete="SET NULL"), nullable=True
    )
    root_id = db.Column(
        db.Integer, ForeignKey("comments.id", ondelete="SET NULL"), nullable=True
    )
    body = db.Column(Text, nullable=False)

    card: Mapped["Card"] = relationship("Card", back_populates="comments")
    author: Mapped["User"] = relationship("User", back_populates="comments")
    parent: Mapped["Comment"] = relationship(
        "Comment", remote_side="Comment.id", backref=backref("children", cascade="all")
    )
    root: Mapped["Comment"] = relationship("Comment", remote_side="Comment.id")

    __table_args__ = (
        CheckConstraint(
            "parent_id IS NULL OR parent_id <> id", name="ck_comments_no_self_parent"
        ),
        Index(
            "ix_comments_card_root_parent_created",
            "card_id",
            "root_id",
            "parent_id",
            "created_at",
        ),
        Index("ix_comments_card_created_desc", "card_id", text("created_at DESC")),
        Index("ix_comments_updated_at", "updated_at"),
    )
