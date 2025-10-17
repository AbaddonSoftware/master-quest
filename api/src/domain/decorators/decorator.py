from __future__ import annotations

from functools import wraps
from typing import Callable

from flask import abort, current_app, g, request
from src.domain.security.permissions import ROLE_DEFAULTS, Permission
from src.domain.selectors.membership import get_role_in_room


def require_permission(permission: Permission, room: str) -> Callable:

    def deco(fn: Callable) -> Callable:

        @wraps(fn)
        def wrapped(*args, **kwargs):
            room_pid = request.args.get(room)
            user_role = get_role_in_room(room_pid)
            permission in ROLE_DEFAULTS.get(user_role) or abort(
                403, f"I'm sorry, {g.user.name}, I'm afraid I can't do that."
            )
            return fn(*args, **kwargs)

        return wrapped

    return deco
