import re
from enum import Enum

from ..exceptions import ValidationError
from .string_validators import validate_identifier as validate_str


def validate_in_enum(
    field: str, allowed_enum: Enum, field_name: str, required: bool = True
):
    field = validate_str(field, field_name, required)
    if field is None:
        return None
    field = (field or "").strip().upper()
    allowed = [item.value for item in allowed_enum]
    if field not in allowed:
        raise ValidationError(
            details=f"'{field_name}' must be one of: {', '.join(allowed)} and was {field}."
        )
    return field
