import re
from enum import Enum

from ..exceptions import ValidationError


def _require_presence_int(
    value: int, field: str, *, required: bool = True
) -> int | None:
    """Ensure presence if required; otherwise allow None."""
    if value is None:
        if required:
            raise ValidationError(f"'{field}' is required.")
        return None
    return value


def _ensure_int_type(value: int | None, field: str):
    if type(value) is int:
        return value
    raise ValidationError(
        f"'field' must be int type and received {type(value)} instead."
    )


def _enforce_int_bounds(
    value: int, field: str, min_value: int | None = None, max_value: int | None = None
):
    min_v = -float("inf") if min_value is None else min_value
    max_v = float("inf") if max_value is None else max_value
    if min_v <= value <= max_v:
        return value
    raise ValidationError(
        f"'{field}' must be in range of {min_v} and {max_v} inclusive."
    )


def validate_int(
    value: int | None,
    field: str,
    required: bool = True,
    min_value: int | None = None,
    max_value: int | None = None,
):
    value = _require_presence_int(value, field, required=required)
    if value is None:
        return None
    value = _ensure_int_type(value, field)
    value = _enforce_int_bounds(value, field, min_value=min_value, max_value=max_value)
    return value
