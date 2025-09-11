from __future__ import annotations

from sqlalchemy import CheckConstraint, Index, UniqueConstraint

from app.extensions import db

from .enums import LaneType
from .mixins import PublicIdMixin, SurrogatePK, TimestampMixin


class Board(db.Model, SurrogatePK, PublicIdMixin, TimestampMixin):
    __tablename__ = "boards"
    __table_args__ = (
        UniqueConstraint("room_id", "name", name="uq_boards_room_name"),
        Index("ix_boards_room_id", "room_id"),
        Index(
            "uq_boards_room_slug",
            "room_id",
            "slug",
            unique=True,
            postgresql_where=db.text("slug IS NOT NULL"),
        ),
    )

    room_id = db.Column(
        db.Integer,
        db.ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.Text, nullable=True)

    room = db.relationship("Room", back_populates="boards")
    columns = db.relationship(
        "BoardColumn",
        back_populates="board",
        cascade="all, delete-orphan",
        order_by="BoardColumn.position",
    )
    lanes = db.relationship(
        "SwimLane",
        back_populates="board",
        cascade="all, delete-orphan",
        order_by="SwimLane.position",
    )
    cards = db.relationship(
        "Card", back_populates="board", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Board id={self.id} public_id={self.public_id} name={self.name!r}>"


class BoardColumn(db.Model, SurrogatePK, TimestampMixin):
    __tablename__ = "board_columns"
    __table_args__ = (
        UniqueConstraint("board_id", "name", name="uq_board_columns_board_name"),
        Index("ix_board_columns_board_position", "board_id", "position"),
        CheckConstraint("position >= 0", name="ck_board_columns_position_nonneg"),
    )

    board_id = db.Column(
        db.Integer,
        db.ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = db.Column(db.String(64), nullable=False)
    position = db.Column(db.Integer, nullable=False, server_default=db.text("0"))

    board = db.relationship("Board", back_populates="columns")
    cards = db.relationship("Card", back_populates="column", order_by="Card.position")

    def __repr__(self) -> str:
        return f"<BoardColumn id={self.id} board={self.board_id} name={self.name!r} pos={self.position}>"


class SwimLane(db.Model, SurrogatePK, TimestampMixin):
    __tablename__ = "swim_lanes"
    __table_args__ = (
        UniqueConstraint("board_id", "name", name="uq_swim_lanes_board_name"),
        Index("ix_swim_lanes_board_position", "board_id", "position"),
        CheckConstraint("position >= 0", name="ck_swim_lanes_position_nonneg"),
    )

    board_id = db.Column(
        db.Integer,
        db.ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = db.Column(db.String(64), nullable=False)
    type = db.Column(LaneType, nullable=False, server_default="standard")
    position = db.Column(db.Integer, nullable=False, server_default=db.text("0"))

    board = db.relationship("Board", back_populates="lanes")
    cards = db.relationship("Card", back_populates="lane")

    def __repr__(self) -> str:
        return f"<SwimLane id={self.id} board={self.board_id} name={self.name!r} type={self.type} pos={self.position}>"
