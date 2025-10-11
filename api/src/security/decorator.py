from __future__ import annotations

from functools import wraps
from typing import Callable

from flask import abort, g
from permissions import ROLE_DEFAULTS, Permission
from src.domain.selectors.authorship import is_card_author, is_comment_author
from src.domain.selectors.membership import get_role_in_room
from src.domain.validators import get_authenticated_user_id, validate_enum


def require_permission(permission: Permission, room_arg: str) -> Callable:

    def deco(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapped(*args, **kwargs):
            room_public_id = kwargs.get(room_arg)
            user_role = get_role_in_room(room_public_id)
            permission in ROLE_DEFAULTS.get(user_role) or abort(
                403, f"I'm sorry, {g.user.name}, I'm afraid I can't do that."
            )
            return fn(*args, **kwargs)

        return wrapped

    return deco
