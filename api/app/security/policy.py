from __future__ import annotations

from typing import Mapping, Protocol

from .permissions import Permission
from .roles import has_at_least


# --- Helpers  ----------------------------------------------------
class Check(Protocol):
    def __call__(self, role: str, ctx: Mapping[str, object]) -> bool: ...


def any_of(*checks: Check) -> Check:
    def _f(role: str, ctx: Mapping[str, object]) -> bool:
        return any(ch(role, ctx) for ch in checks)

    return _f


def all_of(*checks: Check) -> Check:
    def _f(role: str, ctx: Mapping[str, object]) -> bool:
        return all(ch(role, ctx) for ch in checks)

    return _f


def min_role(level: str) -> Check:
    return lambda role, _ctx: has_at_least(role, level)


def flag(name: str) -> Check:
    return lambda role, ctx: bool(ctx.get(name))


def always() -> Check:
    return lambda role, _ctx: True


# --- Policies -------------------------------------------------------------

# Reusable groups
READ_ANY = min_role("viewer")
MEMBER_OR_ABOVE = min_role("member")
ADMIN_OR_ABOVE = min_role("admin")

POLICY: dict[Permission, Check] = {
    # Viewers can look at things in rooms they are in
    Permission.ROOM_READ: READ_ANY,
    Permission.BOARD_READ: READ_ANY,
    Permission.CARD_READ: READ_ANY,
    # Invitations & kicks: Admin or above
    Permission.ROOM_INVITE: ADMIN_OR_ABOVE,
    Permission.ROOM_KICK: ADMIN_OR_ABOVE,
    # Board & structure: Member or above
    Permission.BOARD_CREATE: MEMBER_OR_ABOVE,
    Permission.BOARD_UPDATE: MEMBER_OR_ABOVE,
    Permission.BOARD_DELETE: MEMBER_OR_ABOVE,
    Permission.BOARD_RESTORE: MEMBER_OR_ABOVE,
    Permission.COLUMN_CREATE: MEMBER_OR_ABOVE,
    Permission.COLUMN_UPDATE: MEMBER_OR_ABOVE,
    Permission.COLUMN_DELETE: MEMBER_OR_ABOVE,
    Permission.LANE_CREATE: MEMBER_OR_ABOVE,
    Permission.LANE_UPDATE: MEMBER_OR_ABOVE,
    Permission.LANE_DELETE: MEMBER_OR_ABOVE,
    Permission.LABEL_MANAGE: MEMBER_OR_ABOVE,
    # Cards: Member or above
    Permission.CARD_CREATE: MEMBER_OR_ABOVE,
    Permission.CARD_UPDATE: MEMBER_OR_ABOVE,
    Permission.CARD_DELETE: MEMBER_OR_ABOVE,
    Permission.CARD_RESTORE: MEMBER_OR_ABOVE,
    Permission.ATTACHMENT_ADD: MEMBER_OR_ABOVE,
    Permission.ATTACHMENT_DELETE: MEMBER_OR_ABOVE,
    Permission.TWEE_UPLOAD: MEMBER_OR_ABOVE,
    # Comments:
    # - create: Member or above
    Permission.COMMENT_CREATE: MEMBER_OR_ABOVE,
    # - update/delete: author OR Admin or above
    Permission.COMMENT_UPDATE: any_of(flag("is_author"), ADMIN_OR_ABOVE),
    Permission.COMMENT_DELETE: any_of(flag("is_author"), ADMIN_OR_ABOVE),
    # Room restore / hard delete / purge: owner-only (explicit flag)
    Permission.ROOM_RESTORE: flag("is_owner"),
    Permission.ROOM_DELETE_HARD: flag("is_owner"),
    Permission.PURGE: flag("is_owner"),
}

# --- Public API ---------------------------------------------------------------


def can(
    *, role: str, permission: Permission, ctx: Mapping[str, object] | None = None
) -> bool:
    """
    Evaluate central policy. `ctx` may include:
      is_author: bool  (for comment/card authored-by checks)
      is_owner:  bool  (room owner)
    """
    check = POLICY.get(permission)
    if check is None:
        return False  # default deny for unknown permission
    return check(role, ctx or {})
