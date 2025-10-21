"""remove unique board per room

Revision ID: d9a6e8a01d9d
Revises: c5f9e8e7c06b
Create Date: 2025-10-21 04:45:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d9a6e8a01d9d"
down_revision: Union[str, Sequence[str], None] = "c5f9e8e7c06b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_boards_one_active_per_room")


def downgrade() -> None:
    op.create_index(
        "uq_boards_one_active_per_room",
        "boards",
        ["room_id"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
