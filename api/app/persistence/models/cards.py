from __future__ import annotations

from app.extensions import db
from sqlalchemy import CheckConstraint, Index

from .enums import AttachmentKind
from ..orm.mixins import DeletedAtMixin, PublicIdMixin, SurrogatePK, TimestampMixin


class Card(db.Model, SurrogatePK, PublicIdMixin, TimestampMixin, DeletedAtMixin):
    __tablename__ = "cards"
    __table_args__ = (
        Index("ix_cards_board_column_pos", "board_id", "column_id", "position"),
        Index("ix_cards_swimlane", "swim_lane_id"),
        Index("ix_cards_due", "due_at"),
        CheckConstraint("position >= 0", name="ck_cards_position_nonneg"),
    )
    board_id = db.Column(
        db.Integer, db.ForeignKey("boards.id", ondelete="CASCADE"), nullable=False
    )
    column_id = db.Column(
        db.Integer,
        db.ForeignKey("board_columns.id", ondelete="CASCADE"),
        nullable=False,
    )
    swim_lane_id = db.Column(
        db.Integer, db.ForeignKey("swim_lanes.id", ondelete="SET NULL")
    )
    title = db.Column(db.String(160), nullable=False)
    body = db.Column(db.Text)
    position = db.Column(db.Integer, nullable=False, server_default=db.text("0"))
    due_at = db.Column(db.DateTime(timezone=True))
    author_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), index=True
    )

    # simple relationships; lists of children filtered on their own models
    # (relationship collections on Board already filter Card.deleted_at)


class CardAssignment(db.Model):
    __tablename__ = "card_assignments"
    card_id = db.Column(
        db.Integer, db.ForeignKey("cards.id", ondelete="CASCADE"), primary_key=True
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    assigned_at = db.Column(
        db.DateTime(timezone=True), server_default=db.func.now(), nullable=False
    )
