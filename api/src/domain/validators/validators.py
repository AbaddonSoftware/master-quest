from enum import Enum

from flask import abort, g


def _require_field(field: str | int | bool, field_name: str):
    if field is None:
        abort(400, f"'{field_name}' must be specified.")


def validate_string_field(
    field: str | None, field_name: str, required: bool = True
) -> str | None:
    if required:
        _require_field(field, field_name)
    if field is None:
        return None
    isinstance(field, str) or abort(400, f"'{field_name}' must be a string.")
    field = field.strip()
    return field


def validate_int_field(
    field: int | None, field_name: str, required: bool = True
) -> int | None:
    if required:
        _require_field(field, field_name)
    if field is None:
        return None
    isinstance(field, int) or abort(400, f"'{field_name}' must be an integer.")
    return field


def get_authenticated_user_id() -> int:
    user = getattr(g, "user", None)
    has_user_id = user and user.id is not None
    has_user_id or abort(401, "No user found, login to use this API.")
    return user.id


def validate_string_length(
    input_string: str, min_len: int, max_len: int, field_name: str
):
    length_of_value = len(input_string)
    is_str_bounded = min_len <= length_of_value <= max_len
    is_str_bounded or abort(
        400, f"'{field_name}' must be between {min_len} and {max_len}"
    )


def validate_in_enum(
    input_string: str, enum_type: Enum, field_name: str, required: bool = True
) -> str | None:
    if required:
        _require_field(input_string, field_name)
    if input_string is not None:
        input_string = (input_string or "").strip().upper()
        allowed_values = [item.value for item in enum_type]
        is_value_in_enum = input_string in allowed_values
        is_value_in_enum or abort(
            400, f"'{field_name}' must be one of: {', '.join(allowed_values)}"
        )
        return input_string
    return None
