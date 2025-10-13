from __future__ import annotations

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, backref, relationship
from src.extensions import db
from src.persistence.orm.mixins import DeletedAtMixin, SurrogatePK, TimestampMixin


class Comment(db.Model, SurrogatePK, TimestampMixin, DeletedAtMixin):
    __tablename__ = "comments"

    card_id = Column(
        Integer, ForeignKey("cards.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    parent_id = Column(Integer, nullable=True, index=True)
    root_id = Column(Integer, nullable=True, index=True)

    body = Column(Text, nullable=False)

    parent: Mapped["Comment"] = relationship(
        "Comment",
        primaryjoin="Comment.parent_id == Comment.id",
        foreign_keys=lambda: [Comment.parent_id],
        remote_side=lambda: [Comment.id],
        backref=backref("children", cascade="all, delete-orphan"),
    )

    # Thread root (top-level). View-only so ORM doesn’t try to manage it via this rel.
    root: Mapped["Comment"] = relationship(
        "Comment",
        primaryjoin="Comment.root_id == Comment.id",
        foreign_keys=lambda: [Comment.root_id],
        remote_side=lambda: [Comment.id],
        viewonly=True,
    )

    author = relationship("User", back_populates="comments", foreign_keys=[author_id])
    card = relationship("Card", back_populates="comments", foreign_keys=[card_id])

    __table_args__ = (
        # Ensure (id, card_id) can be referenced together
        UniqueConstraint("id", "card_id", name="uq_comments_id_card"),
        # Parent must be on same card
        ForeignKeyConstraint(
            ["parent_id", "card_id"],
            ["comments.id", "comments.card_id"],
            name="fk_comments_parent_same_card",
            ondelete="SET NULL",
        ),
        # Root must be on same card
        ForeignKeyConstraint(
            ["root_id", "card_id"],
            ["comments.id", "comments.card_id"],
            name="fk_comments_root_same_card",
            ondelete="SET NULL",
        ),
        CheckConstraint(
            "parent_id IS NULL OR parent_id <> id", name="ck_comments_no_self_parent"
        ),
        CheckConstraint(
            "(parent_id IS NULL AND root_id = id) OR (parent_id IS NOT NULL AND root_id IS NOT NULL)",
            name="ck_comments_root_invariant",
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
