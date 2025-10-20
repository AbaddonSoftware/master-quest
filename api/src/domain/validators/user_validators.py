from flask import g

from ..exceptions import ValidationError


def validate_user_logged_in():
    user = getattr(g, "user", None)
    if user is not None and getattr(user, "id", None) is not None:
        return user.id
    raise ValidationError("No user found, You must login.")
