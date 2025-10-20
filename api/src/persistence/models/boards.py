from __future__ import annotations

from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    UniqueConstraint,
    and_,
    func,
    text,
)
from sqlalchemy.orm import Mapped, backref, foreign, mapped_column, relationship, declared_attr
from src.extensions import db
from src.persistence.orm.mixins import (
    DeletedAtMixin,
    PublicIdMixin,
    SurrogatePK,
    TimestampMixin,
)


class Board(db.Model, SurrogatePK, PublicIdMixin, TimestampMixin, DeletedAtMixin):
    __tablename__ = "boards"
    room_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    room: Mapped["Room"] = relationship("Room", back_populates="boards")
    columns: Mapped[list["BoardColumn"]] = relationship(
        "BoardColumn",
        back_populates="board",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="BoardColumn.position",
    )

@declared_attr.directive
def __table_args__(cls):
    return (
    Index(
        "uq_boards_one_active_per_room",
        cls.room_id,
        unique=True,
        postgresql_where=cls.deleted_at.is_(None),
    ),
    Index(
        "uq_boards_room_lower_name",
        cls.room_id,
        func.lower(cls.name),
        unique=True,
    ),
    )



class BoardColumn(db.Model, SurrogatePK, TimestampMixin, DeletedAtMixin):
    __tablename__ = "board_columns"

    board_id: Mapped[int] = mapped_column(
        db.Integer,
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parent_id: Mapped[int] = mapped_column(Integer, nullable=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    position: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    wip_limit: Mapped[int] = mapped_column(Integer, nullable=True)
    column_type: Mapped[str] = mapped_column(
        String(128), nullable=False, server_default=text("'standard'")
    )
    board: Mapped["Board"] = relationship(
        "Board",
        back_populates="columns",
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
    )
