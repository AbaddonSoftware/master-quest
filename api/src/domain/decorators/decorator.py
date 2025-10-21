from __future__ import annotations

from functools import wraps
from typing import Callable

from flask import abort, current_app, g, request
from ..exceptions import ForbiddenError, ValidationError
from ..security.permissions import ROLE_DEFAULTS, Permission
from ..selectors.membership import get_role_in_room


def require_permission(
    permission: Permission, room_param: str = "room_public_id"
) -> Callable:

    def deco(fn: Callable) -> Callable:

        @wraps(fn)
        def wrapped(*args, **kwargs):
            room_pid = kwargs.get(room_param)
            if not room_pid:
                raise ValidationError(f"Missing route parameter '{room_param}'.")
            user_role = get_role_in_room(room_pid)
            if not permission in ROLE_DEFAULTS.get(user_role):
                raise ForbiddenError(
                    f"I'm sorry, {g.user.name}, I'm afraid I can't do that."
                )
            return fn(*args, **kwargs)

        return wrapped

    return deco
