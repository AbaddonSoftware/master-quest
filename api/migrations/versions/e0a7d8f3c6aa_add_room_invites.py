"""add room invites

Revision ID: e0a7d8f3c6aa
Revises: d9a6e8a01d9d
Create Date: 2025-01-18 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e0a7d8f3c6aa"
down_revision: Union[str, Sequence[str], None] = "d9a6e8a01d9d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "invites",
        sa.Column("room_id", sa.Integer(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("code", sa.String(length=40), nullable=False, unique=True),
        sa.Column(
            "role",
            sa.Enum(
                "OWNER",
                "ADMIN",
                "MEMBER",
                "VIEWER",
                name="role_type",
                create_constraint=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "redemption_max",
            sa.Integer(),
            server_default="1",
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("public_id", sa.UUID(as_uuid=True), nullable=False, unique=True),
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
        sa.CheckConstraint(
            "redemption_max >= 1",
            name="ck_invites_redemption_max_positive",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"], ["users.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["room_id"], ["rooms.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_invites_room_id"), "invites", ["room_id"], unique=False)
    op.create_index(
        op.f("ix_invites_created_by_id"),
        "invites",
        ["created_by_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_invites_deleted_at"), "invites", ["deleted_at"], unique=False
    )
    op.create_index(
        op.f("ix_invites_deleted_by_id"),
        "invites",
        ["deleted_by_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_invites_expires_at"), "invites", ["expires_at"], unique=False
    )

    op.create_table(
        "invite_redemptions",
        sa.Column("invite_id", sa.Integer(), nullable=False),
        sa.Column("redeemed_by_id", sa.Integer(), nullable=True),
        sa.Column(
            "redeemed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
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
        sa.ForeignKeyConstraint(
            ["invite_id"], ["invites.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["redeemed_by_id"], ["users.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "invite_id",
            "redeemed_by_id",
            name="uq_invite_redemptions_invitee_once",
        ),
    )
    op.create_index(
        op.f("ix_invite_redemptions_invite_id"),
        "invite_redemptions",
        ["invite_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_invite_redemptions_redeemed_by_id"),
        "invite_redemptions",
        ["redeemed_by_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_invite_redemptions_redeemed_by_id"), table_name="invite_redemptions")
    op.drop_index(op.f("ix_invite_redemptions_invite_id"), table_name="invite_redemptions")
    op.drop_table("invite_redemptions")
    op.drop_index(op.f("ix_invites_expires_at"), table_name="invites")
    op.drop_index(op.f("ix_invites_deleted_by_id"), table_name="invites")
    op.drop_index(op.f("ix_invites_deleted_at"), table_name="invites")
    op.drop_index(op.f("ix_invites_created_by_id"), table_name="invites")
    op.drop_index(op.f("ix_invites_room_id"), table_name="invites")
    op.drop_table("invites")
