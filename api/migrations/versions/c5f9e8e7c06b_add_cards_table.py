"""add cards table

Revision ID: c5f9e8e7c06b
Revises: b9df84ad9bda
Create Date: 2025-10-20 22:32:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c5f9e8e7c06b"
down_revision: Union[str, Sequence[str], None] = "b9df84ad9bda"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cards",
        sa.Column("board_id", sa.Integer(), nullable=False),
        sa.Column("column_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "position", sa.Integer(), server_default=sa.text("0"), nullable=False
        ),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("public_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by_id", sa.Integer(), nullable=True),
        sa.CheckConstraint("position >= 0", name="ck_cards_position_nonneg"),
        sa.ForeignKeyConstraint(["board_id"], ["boards.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["column_id"], ["board_columns.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("column_id", "position", name="uq_cards_column_position"),
        sa.UniqueConstraint("public_id"),
    )
    op.create_index(
        "ix_cards_board_column_position",
        "cards",
        ["board_id", "column_id", "position"],
        unique=False,
    )
    op.create_index(op.f("ix_cards_deleted_at"), "cards", ["deleted_at"], unique=False)
    op.create_index(
        op.f("ix_cards_deleted_by_id"), "cards", ["deleted_by_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_cards_deleted_by_id"), table_name="cards")
    op.drop_index(op.f("ix_cards_deleted_at"), table_name="cards")
    op.drop_index("ix_cards_board_column_position", table_name="cards")
    op.drop_table("cards")
