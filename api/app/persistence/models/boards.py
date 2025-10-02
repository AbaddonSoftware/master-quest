from __future__ import annotations

from app.extensions import db
from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, backref, relationship

from ..orm.mixins import DeletedAtMixin, PublicIdMixin, SurrogatePK, TimestampMixin
from .enums import LaneType


class Board(db.Model, SurrogatePK, PublicIdMixin, TimestampMixin, DeletedAtMixin):
    __tablename__ = "boards"

    room_id = db.Column(
        db.Integer,
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = db.Column(String(120), nullable=False)

    room: Mapped["Room"] = relationship("Room", back_populates="boards")

    columns: Mapped[list["BoardColumn"]] = relationship(
        "BoardColumn",
        back_populates="board",
        cascade="all, delete-orphan",
        passive_deletes=True,
        primaryjoin="and_(Board.id==foreign(BoardColumn.board_id), BoardColumn.deleted_at.is_(None))",
        order_by="BoardColumn.position",
    )
    lanes: Mapped[list["SwimLane"]] = relationship(
        "SwimLane",
        back_populates="board",
        cascade="all, delete-orphan",
        passive_deletes=True,
        primaryjoin="and_(Board.id==foreign(SwimLane.board_id), SwimLane.deleted_at.is_(None))",
        order_by="SwimLane.position",
    )
    cards: Mapped[list["Card"]] = relationship(
        "Card",
        back_populates="board",
        cascade="all, delete-orphan",
        passive_deletes=True,
        primaryjoin="and_(Board.id==foreign(Card.board_id), Card.deleted_at.is_(None))",
    )

    __table_args__ = (
        Index(
            "uq_boards_room_id_active",
            "room_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )


class BoardColumn(db.Model, SurrogatePK, TimestampMixin, DeletedAtMixin):
    __tablename__ = "board_columns"

    board_id = db.Column(
        db.Integer,
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parent_id = db.Column(db.Integer, nullable=True)
    title = db.Column(String(128), nullable=False)
    position = db.Column(db.Integer, nullable=False, server_default=text("0"))
    wip_limit = db.Column(db.Integer, nullable=True)

    board: Mapped["Board"] = relationship("Board", back_populates="columns")
    parent: Mapped["BoardColumn"] = relationship(
        "BoardColumn",
        remote_side="BoardColumn.id",
        backref=backref("children", cascade="all, delete-orphan"),
    )

    __table_args__ = (
        CheckConstraint("position >= 0", name="ck_columns_position_nonneg"),
        CheckConstraint(
            "wip_limit IS NULL OR wip_limit >= 0", name="ck_columns_wip_nonneg"
        ),
        CheckConstraint(
            "parent_id IS NULL OR parent_id <> id", name="ck_columns_no_self_parent"
        ),
        UniqueConstraint("id", "board_id", name="uq_columns_id_board"),
        ForeignKeyConstraint(
            ["parent_id", "board_id"],
            ["board_columns.id", "board_columns.board_id"],
            name="fk_columns_parent_same_board",
            ondelete="SET NULL",
            use_alter=True,
        ),
        Index(
            "uq_columns_board_parent_position_active",
            "board_id",
            "parent_id",
            "position",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index("ix_columns_board_parent_position", "board_id", "parent_id", "position"),
        Index(
            "ix_columns_board_active",
            "board_id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )


class SwimLane(db.Model, SurrogatePK, TimestampMixin, DeletedAtMixin):
    __tablename__ = "swim_lanes"

    board_id = db.Column(
        db.Integer,
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = db.Column(String(128), nullable=False)
    position = db.Column(db.Integer, nullable=False, server_default=text("0"))
    lane_type = db.Column(LaneType, nullable=False, server_default=text("'standard'"))

    board: Mapped["Board"] = relationship("Board", back_populates="lanes")

    __table_args__ = (
        CheckConstraint("position >= 0", name="ck_lanes_position_nonneg"),
        UniqueConstraint("id", "board_id", name="uq_lanes_id_board"),
        Index(
            "uq_lanes_board_position_active",
            "board_id",
            "position",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_lanes_board_active",
            "board_id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )
