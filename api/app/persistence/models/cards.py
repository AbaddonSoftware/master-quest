from __future__ import annotations
from app.extensions import db
from sqlalchemy import Index, CheckConstraint
from .mixins import SurrogatePK, TimestampMixin, PublicIdMixin

class Card(db.Model, SurrogatePK, PublicIdMixin, TimestampMixin):
    __tablename__ = "cards"
    __table_args__ = (
        Index("ix_cards_board_column_pos", "board_id", "column_id", "position"),
        Index("ix_cards_swimlane", "swim_lane_id"),
        Index("ix_cards_due", "due_at"),
        CheckConstraint("position >= 0", name="ck_cards_position_nonneg"),
    )

    board_id = db.Column(db.Integer, db.ForeignKey("boards.id", ondelete="CASCADE"), nullable=False)
    column_id = db.Column(db.Integer, db.ForeignKey("board_columns.id", ondelete="CASCADE"), nullable=False)
    swim_lane_id = db.Column(db.Integer, db.ForeignKey("swim_lanes.id", ondelete="SET NULL"))

    title = db.Column(db.String(160), nullable=False)
    body = db.Column(db.Text)
    position = db.Column(db.Integer, nullable=False, server_default=db.text("0"))
    due_at = db.Column(db.DateTime(timezone=True))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), index=True)

    board = db.relationship("Board", back_populates="cards")
    column = db.relationship("BoardColumn", back_populates="cards")
    lane = db.relationship("SwimLane", back_populates="cards")
    author = db.relationship("User")

    comments = db.relationship("CardComment", back_populates="card", cascade="all, delete-orphan", order_by="CardComment.created_at")
    assignments = db.relationship("CardAssignment", back_populates="card", cascade="all, delete-orphan")
    attachments = db.relationship("CardAttachment", back_populates="card", cascade="all, delete-orphan")
    labels = db.relationship("Label", secondary="card_labels", back_populates="cards")

    def __repr__(self) -> str:
        return f"<Card id={self.id} public_id={self.public_id} title={self.title!r} pos={self.position}>"

class CardAssignment(db.Model):
    __tablename__ = "card_assignments"
    card_id = db.Column(db.Integer, db.ForeignKey("cards.id", ondelete="CASCADE"), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    assigned_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)

    card = db.relationship("Card", back_populates="assignments")
    user = db.relationship("User")

    def __repr__(self) -> str:
        return f"<CardAssignment card={self.card_id} user={self.user_id}>"
