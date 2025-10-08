from __future__ import annotations

from app.extensions import db
from app.persistence.orm.mixins import PublicIdMixin, SurrogatePK, TimestampMixin
from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, relationship


class User(db.Model, SurrogatePK, PublicIdMixin, TimestampMixin):
    __tablename__ = "users"
    name = db.Column(String(128), nullable=False, unique=False)
    preferred_name = db.Column(String(128), nullable=True, unique=True)
    email = db.Column(CITEXT, index=True)
    terms_accepted_at = db.Column(db.DateTime(timezone=True), nullable=True)
    last_login_at = db.Column(db.DateTime(timezone=True), nullable=False)
    is_guest = db.Column(
        db.Boolean, nullable=False, server_default=text("false"), index=True
    )
    expires_at = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    identities: Mapped[list["Identity"]] = relationship(
        "Identity",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    ownerships: Mapped[list["Room"]] = relationship(
        "Room",
        back_populates="owner",
        cascade="save-update, merge",
        passive_deletes=True,
    )
    memberships: Mapped[list["RoomMember"]] = relationship(
        "RoomMember",
        back_populates="user",
        cascade="save-update, merge",
        passive_deletes=True,
    )
    # # comments: Mapped[list["Comment"]] = relationship(
    #     "Comment",
    #     back_populates="author",
    #     cascade="save-update, merge",
    #     passive_deletes=True,
    # )

    __table_args__ = (
        CheckConstraint("length(email) <= 320", name="ck_users_email_length"),
        Index(
            "uq_users_email_lower",
            func.lower(email),
            unique=True,
            postgresql_where=email.isnot(None),
        ),
        Index(
            "uq_users_name_lower",
            func.lower(name),
            unique=False,
            postgresql_where=name.isnot(None),
        ),
        CheckConstraint(
            "(is_guest = false) OR (expires_at IS NOT NULL)",
            name="ck_users_guest_requires_expires_at",
        ),
        Index(
            "ix_users_expiring_guests_active",
            "expires_at",
            postgresql_where=text("is_guest = true"),
        ),
    )


class Identity(db.Model, SurrogatePK, TimestampMixin):
    __tablename__ = "identities"

    user_id = db.Column(
        db.Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider = db.Column(String(50), nullable=False)
    subject = db.Column(String(255), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="identities")

    __table_args__ = (
        UniqueConstraint("provider", "subject", name="uq_identities_provider_subject"),
    )
