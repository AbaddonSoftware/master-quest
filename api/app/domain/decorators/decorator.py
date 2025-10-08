from __future__ import annotations

from functools import wraps
from typing import Callable

from app.domain.security.permissions import ROLE_DEFAULTS, Permission
from app.domain.selectors.membership import get_role_in_room
from flask import abort, g


def require_permission(permission: Permission, room_arg: str) -> Callable:

    def deco(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapped(*args, **kwargs):
            room_public_id = kwargs.get(room_arg)
            user_role = get_role_in_room(room_public_id)
            username = g.user.name
            permission in ROLE_DEFAULTS.get(user_role) or abort(
                403, f"I'm sorry, {username}, I'm afraid I can't do that."
            )
            return fn(*args, **kwargs)

        return wrapped

    return deco
