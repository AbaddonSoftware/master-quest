from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

# --- Mixins ----------------------------------------------------------------------


class SurrogatePK:
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


class PublicIdMixin:
    public_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )


class CreatorMixin:
    created_by_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=False,
    )


class TimestampMixin:
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


def _ensure_aware(dt: datetime) -> datetime:
    """Return a tz-aware datetime. If naive, assume UTC; otherwise return as-is."""
    is_aware = (dt.tzinfo is not None) and (dt.utcoffset() is not None)
    return dt if is_aware else dt.replace(tzinfo=timezone.utc)


class DeletedAtMixin:
    """Soft delete support. Null = active; Non-null = soft-deleted."""

    deleted_at = Column(DateTime(timezone=True), index=True)
    deleted_by_id = Column(Integer, nullable=True, index=True)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(
        self, actor_id: int | None = None, timestamp: datetime | None = None
    ) -> None:
        self.deleted_by_id = actor_id
        self.deleted_at = func.now() if timestamp is None else _ensure_aware(timestamp)

    def restore(self):
        self.deleted_by_id = None
        self.deleted_at = None
