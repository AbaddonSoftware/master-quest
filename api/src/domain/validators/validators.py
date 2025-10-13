import re
from enum import Enum

from flask import abort, g

ALLOWED_PATTERNS = {
    "letters_and_underscore": r"[A-Za-z_]+",
    "alphanumeric_spaces_and_underscore": r"[A-Za-z0-9_\s]+",  # TODO: simple for now, will expand.
}


def validate_str(
    field: str | None,
    field_name: str,
    required: bool = True,
    min_len: int = 3,
    max_len: int = 128,
    pattern=ALLOWED_PATTERNS.get("letters_and_underscore"),
):
    is_valid = lambda f: type(f) is str and f.strip()
    if field is None:
        return None if not required else abort(400, f"'{field_name}' is required.")
    if is_valid(field):
        field = field.strip()
        if not re.fullmatch(pattern, field):
            abort(
                400,
                f"'{field_name}' may only contain characters conforming to {pattern}.",
            )
        is_bound = min_len <= len(field) <= max_len
        if not is_bound:
            abort(
                400,
                f"'{field_name}' must be between {min_len} and {max_len} characters.",
            )
        return field
    abort(400, f"'{field_name}' must be a string and received {type(field)}.")


def validate_int(
    field: int | None,
    field_name: str,
    required: bool = True,
    min_len: int = 0,
    max_len: int = 4000,
):
    is_valid = lambda f: type(f) is int
    if field is None:
        return None if not required else abort(400, f"'{field_name}' is required.")
    if is_valid(field):
        is_bound = min_len <= field <= max_len
        if not is_bound:
            abort(
                400,
                f"'{field_name}' must be between {min_len} and {max_len}.",
            )
        return field
    abort(400, f"'{field_name}' must be an integer and received {type(field)}.")


def validate_in_enum(
    field: str, allowed_enum: Enum, field_name: str, required: bool = True
):
    field = validate_str(field, field_name, required)
    if field is None:
        return None
    field = (field or "").strip().upper()
    allowed = [item.value for item in allowed_enum]
    field in allowed or abort(
        400, f"'{field_name}' must be one of: {', '.join(allowed)} and was {field}."
    )
    return field


def validate_user_logged_in():
    user = getattr(g, "user", None)
    if user is not None and getattr(user, "id", None) is not None:
        return user.id
    abort(401, "No user found, You must login.")
