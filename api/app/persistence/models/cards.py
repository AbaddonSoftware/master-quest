from __future__ import annotations

from app.extensions import db
from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, backref, relationship

from app.persistence.orm.mixins import DeletedAtMixin, SurrogatePK, TimestampMixin


class Card(db.Model, SurrogatePK, TimestampMixin, DeletedAtMixin):
    __tablename__ = "cards"

    board_id = db.Column(
        db.Integer,
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    column_id = db.Column(db.Integer, nullable=True, index=True)  # composite FK below
    lane_id = db.Column(db.Integer, nullable=True, index=True)  # composite FK below
    title = db.Column(String(255), nullable=False)
    description = db.Column(Text, nullable=True)
    position = db.Column(db.Integer, nullable=False, server_default=text("0"))
    assignees: Mapped[list["User"]] = relationship(
        "User",
        secondary="card_assignments",
        backref=backref("assigned_cards", lazy="selectin"),
        lazy="selectin",
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="card",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    attachments: Mapped[list["CardAttachment"]] = relationship(
        "CardAttachment",
        back_populates="card",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        CheckConstraint("position >= 0", name="ck_cards_position_nonneg"),
        Index(
            "uq_cards_column_position_active",
            "column_id",
            "position",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index("ix_cards_board_column_position", "board_id", "column_id", "position"),
        Index("ix_cards_board_column_lane", "board_id", "column_id", "lane_id"),
        Index(
            "ix_cards_board_active",
            "board_id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        ForeignKeyConstraint(
            ["column_id", "board_id"],
            ["board_columns.id", "board_columns.board_id"],
            ondelete="CASCADE",
            name="fk_cards_column_same_board",
        ),
        ForeignKeyConstraint(
            ["lane_id", "board_id"],
            ["swim_lanes.id", "swim_lanes.board_id"],
            ondelete="SET NULL",
            name="fk_cards_lane_same_board",
        ),
    )


class CardAssignment(db.Model):
    __tablename__ = "card_assignments"

    user_id = db.Column(
        db.Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    card_id = db.Column(
        db.Integer,
        ForeignKey("cards.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    assigned_at = db.Column(
        db.DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (Index("ix_card_assignments_card", "card_id"),)
