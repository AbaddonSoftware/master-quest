from enum import Enum
from flask import abort, g
from typing import Callable


def _must_exist_(field: str|int|bool|None, field_name: str):
    if field == None:
        abort(400, f"'{field_name}' must be specified.")

def _must_not_be_empty_str(field: str|int|bool|None, field_name: str):
    if field == "":
        abort(400, f"'{field_name}' must not be an empty string.")

def _require_field(field, field_name):
    if field == None:
        abort(400, f"'{field_name}' must be specified.")


def validate_string_field(
    field: str | None, field_name: str, required: bool = True
) -> str | None:
    if required:
        _require_field(field, field_name)
    elif field == None:
        return None
    if not isinstance(field, str) or field == "":
        abort(400, f"'{field_name}' must be a non-empty string")
    return field.strip()
    

def validate_int_field(
    field: int | None, field_name: str, required: bool = True
) -> int | None:
    if required:
        _require_field(field, field_name)
    if field is None:
        return None
    if type(field) is not int:
        abort(400, f"'{field_name}' must be an integer.")
    return field


def get_authenticated_user_id() -> int:
    user = getattr(g, "user", None)
    if user is not None and getattr(user, "id", None) is not None:
        return user.id
    abort(401, "No user found, login to use this api.")


def validate_string_length(
    field: str, min_len: int, max_len: int, field_name: str
):
    length_of_value = len(field)
    is_str_bounded = min_len <= length_of_value <= max_len
    is_str_bounded or abort(
        400, f"'{field_name}' must be between {min_len} and {max_len}"
    )
    return field


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
