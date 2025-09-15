from __future__ import annotations

from app.extensions import db
from sqlalchemy import Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from ..orm.mixins import SurrogatePK, TimestampMixin


class User(db.Model, SurrogatePK, TimestampMixin):
    __tablename__ = "users"
    email = db.Column(db.String(255), unique=True, nullable=True, index=True)
    display_name = db.Column(db.String(120), nullable=False)
    avatar_url = db.Column(db.Text, nullable=True)
    last_login_at = db.Column(db.DateTime(timezone=True))
    terms_accepted_at = db.Column(db.DateTime(timezone=True))

    identities = db.relationship(
        "Identity", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} name={self.display_name!r}>"


class Identity(db.Model, SurrogatePK, TimestampMixin):
    __tablename__ = "identities"
    __table_args__ = (
        UniqueConstraint("provider", "subject", name="uq_identity_provider_subject"),
        Index("ix_identities_user_id_provider", "user_id", "provider"),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider = db.Column(db.String(40), nullable=False)  # "google", "github", "discord"
    subject = db.Column(db.String(255), nullable=False)  # stable provider user id / sub
    email_at_auth = db.Column(db.String(255))
    profile_json = db.Column(JSONB)

    user = db.relationship("User", back_populates="identities")

    def __repr__(self) -> str:
        return f"<Identity {self.provider}:{self.subject} user={self.user_id}>"
