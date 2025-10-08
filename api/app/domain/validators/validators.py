from flask import g, abort
from enum import Enum

def require_field(field: str, field_name: str):
    field = (field or "").strip()
    field or abort(400, f"'{field_name}' must be specified.")
    return field

def get_authenticated_user_id() -> int:
    user = getattr(g, "user", None)
    has_user_id = user and user.id is not None
    has_user_id or abort(401, "No user found, login to use this API.")
    return user.id

def validate_str_length(input_string: str, min_len: int, max_len: int, field_name: str):
    length_of_value = len(input_string)
    is_str_bounded = min_len <= length_of_value <= max_len
    is_str_bounded or abort(400, f"'{field_name}' must be between {min_len} and {max_len}")

def validate_enum(input_string: str, enum_type: Enum, field_name: str) -> str:
    input_string = (input_string or "").strip().upper()
    allowed_values = [item.value for item in enum_type]
    is_value_in_enum = input_string in allowed_values
    is_value_in_enum or abort(400, f"'{field_name}' must be one of: {', '.join(allowed_values)}")
    return input_string
    


