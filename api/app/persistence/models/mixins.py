from __future__ import annotations

import uuid

from app.extensions import db


class SurrogatePK:
    id = db.Column(db.Integer, primary_key=True)


class PublicIdMixin:
    # Opaque, URL-safe external ID; prefer in APIs/links instead of int PKs
    public_id = db.Column(
        db.dialects.postgresql.UUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        index=True,
    )


class TimestampMixin:
    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False,
    )
