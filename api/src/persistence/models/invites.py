from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ...domain.security.permissions import RoleType
from ...extensions import db
from ...persistence.orm.mixins import (
    DeletedAtMixin,
    PublicIdMixin,
    SurrogatePK,
    TimestampMixin,
)


class Invite(db.Model, SurrogatePK, PublicIdMixin, TimestampMixin, DeletedAtMixin):
    __tablename__ = "invites"

    room_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    code: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    role: Mapped[RoleType] = mapped_column(
        Enum(RoleType, name="role_type", create_constraint=False),
        nullable=False,
    )
    redemption_max: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1"
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    room: Mapped["Room"] = relationship("Room", back_populates="invites")
    creator: Mapped["User | None"] = relationship(
        "User", back_populates="created_invites"
    )
    redemptions: Mapped[list["InviteRedemption"]] = relationship(
        "InviteRedemption",
        back_populates="invite",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        CheckConstraint(
            "redemption_max >= 1", name="ck_invites_redemption_max_positive"
        ),
    )


class InviteRedemption(db.Model, SurrogatePK, TimestampMixin):
    __tablename__ = "invite_redemptions"

    invite_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("invites.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    redeemed_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    redeemed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    invite: Mapped[Invite] = relationship("Invite", back_populates="redemptions")
    redeemed_by: Mapped["User | None"] = relationship(
        "User", back_populates="invite_redemptions"
    )

    __table_args__ = (
        UniqueConstraint(
            "invite_id",
            "redeemed_by_id",
            name="uq_invite_redemptions_invitee_once",
        ),
    )
