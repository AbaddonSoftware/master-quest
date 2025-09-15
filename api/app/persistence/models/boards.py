from __future__ import annotations

from app.extensions import db
from sqlalchemy import CheckConstraint, Index, UniqueConstraint, and_
from sqlalchemy.orm import foreign

from .enums import LaneType, Role
from ..orm.mixins import DeletedAtMixin, PublicIdMixin, SurrogatePK, TimestampMixin


class Board(db.Model, SurrogatePK, PublicIdMixin, TimestampMixin, DeletedAtMixin):
    __tablename__ = "boards"
    __table_args__ = (
        UniqueConstraint(
            "room_id", "name", name="uq_boards_room_name"
        ),  # migrate to partial unique
        Index("ix_boards_room_id", "room_id"),
        Index(
            "uq_boards_room_slug",
            "room_id",
            "slug",
            unique=True,
            postgresql_where=db.text("slug IS NOT NULL AND deleted_at IS NULL"),
        ),
    )
    room_id = db.Column(
        db.Integer, db.ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False
    )
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.Text)

    room = db.relationship("Room")

    columns = db.relationship(
        "BoardColumn",
        primaryjoin="and_(Board.id == foreign(BoardColumn.board_id), BoardColumn.deleted_at.is_(None))",
        order_by="BoardColumn.position",
        lazy="selectin",
    )
    lanes = db.relationship(
        "SwimLane",
        primaryjoin="and_(Board.id == foreign(SwimLane.board_id), SwimLane.deleted_at.is_(None))",
        order_by="SwimLane.position",
        lazy="selectin",
    )
    cards = db.relationship(
        "Card",
        primaryjoin="and_(Board.id == foreign(Card.board_id), Card.deleted_at.is_(None))",
        lazy="selectin",
    )


class BoardColumn(db.Model, SurrogatePK, TimestampMixin, DeletedAtMixin):
    __tablename__ = "board_columns"
    __table_args__ = (
        UniqueConstraint(
            "board_id", "name", name="uq_board_columns_board_name"
        ),  # migrate to partial unique
        Index("ix_board_columns_board_position", "board_id", "position"),
        CheckConstraint("position >= 0", name="ck_board_columns_position_nonneg"),
    )
    board_id = db.Column(
        db.Integer, db.ForeignKey("boards.id", ondelete="CASCADE"), nullable=False
    )
    name = db.Column(db.String(64), nullable=False)
    position = db.Column(db.Integer, nullable=False, server_default=db.text("0"))

    board = db.relationship("Board")


class SwimLane(db.Model, SurrogatePK, TimestampMixin, DeletedAtMixin):
    __tablename__ = "swim_lanes"
    __table_args__ = (
        UniqueConstraint(
            "board_id", "name", name="uq_swim_lanes_board_name"
        ),  # migrate to partial unique
        Index("ix_swim_lanes_board_position", "board_id", "position"),
        CheckConstraint("position >= 0", name="ck_swim_lanes_position_nonneg"),
    )
    board_id = db.Column(
        db.Integer, db.ForeignKey("boards.id", ondelete="CASCADE"), nullable=False
    )
    name = db.Column(db.String(64), nullable=False)
    type = db.Column(
        LaneType,
        nullable=False,
        server_default="standard",
    )
    position = db.Column(db.Integer, nullable=False, server_default=db.text("0"))

    board = db.relationship("Board")
