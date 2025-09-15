from __future__ import annotations

ROLE_ORDER = {
    "owner": 3,
    "admin": 2,
    "member": 1,
    "viewer": 0,
}


def has_at_least(user_role: str, required: str) -> bool:
    """
    Return True if a given user_role is >= required role in the hierarchy.
    Example:
        has_at_least("admin", "member") -> True
        has_at_least("viewer", "member") -> False
    """
    return ROLE_ORDER.get(user_role, -1) >= ROLE_ORDER.get(required, 99)
