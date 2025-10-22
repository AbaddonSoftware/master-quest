from __future__ import annotations

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...extensions import db
from ..orm.mixins import DeletedAtMixin, PublicIdMixin, SurrogatePK, TimestampMixin


class Card(db.Model, SurrogatePK, PublicIdMixin, TimestampMixin, DeletedAtMixin):
    __tablename__ = "cards"

    board_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("boards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    column_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("board_columns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    position: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )

    board: Mapped["Board"] = relationship("Board", back_populates="cards")
    column: Mapped["BoardColumn"] = relationship("BoardColumn", back_populates="cards")

    __table_args__ = (
        CheckConstraint("position >= 0", name="ck_cards_position_nonneg"),
        UniqueConstraint("column_id", "position", name="uq_cards_column_position"),
        Index(
            "ix_cards_board_column_position",
            "board_id",
            "column_id",
            "position",
        ),
    )
