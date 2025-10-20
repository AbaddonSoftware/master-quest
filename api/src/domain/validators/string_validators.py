from __future__ import annotations

import re
import unicodedata
from typing import Optional

from ..exceptions import ValidationError

# === Internal Helpers ========================================================

_ZERO_WIDTH = {"\u200b", "\u200c", "\u200d", "\ufeff"}
_CTRL_EXCEPT_TAB_NL = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")
_CTRL_ALL = re.compile(r"[\x00-\x1F\x7F]")


def _strip_zero_width(value: str) -> str:
    """Remove zero-width and BOM characters."""
    for ch in _ZERO_WIDTH:
        if ch in value:
            return "".join(c for c in value if c not in _ZERO_WIDTH)
    return value


def _reject_control_chars(value: str, *, allow_tabs_newlines: bool) -> None:
    """Raise if disallowed control chars exist."""
    rx = _CTRL_EXCEPT_TAB_NL if allow_tabs_newlines else _CTRL_ALL
    if rx.search(value):
        raise ValidationError("Value contains control characters.")


def _enforce_ascii_only(value: str, field: str) -> str:
    """Reject non-ASCII characters."""
    try:
        value.encode("ascii")
    except UnicodeEncodeError:
        raise ValidationError(
            f"'{field}' may contain only English letters, digits, spaces, and basic symbols."
        )
    return value


def _enforce_length(value: str, field: str, min_len: int, max_len: int) -> str:
    n = len(value)
    if not (min_len <= n <= max_len):
        raise ValidationError(
            f"'{field}' must be between {min_len} and {max_len} characters."
        )
    return value


def _require_non_blank(value: str, field: str) -> str:
    if value.strip() == "":
        raise ValidationError(f"'{field}' cannot be empty or whitespace.")
    return value


# === Regex patterns ==========================================================
ALLOWED_PATTERNS = {
    "letters_and_underscore": r"[A-Za-z_]+",
    "alphanumeric_spaces_and_underscore": r"[A-Za-z0-9_\s]+",  # TODO: simple for now, will expand.
}
USERNAME_RE = re.compile(r"(?a)^[A-Za-z0-9](?:[A-Za-z0-9_-]*[A-Za-z0-9])?$")


# === Profiles ================================================================


def validate_identifier(
    value: Optional[str],
    field: str = "username",
    *,
    required: bool = True,
    min_len: int = 3,
    max_len: int = 32,
) -> Optional[str]:
    """
    English-only identifiers (usernames, slugs).
    - Normalizes to NFKC
    - Removes zero-width chars
    - Rejects controls and non-ASCII
    - Allows mixed case, digits, '-' and '_'
    """
    if value is None:
        if required:
            raise ValidationError(f"'{field}' is required.")
        return None
    if not isinstance(value, str):
        raise ValidationError(f"'{field}' must be a string.")

    value = unicodedata.normalize("NFKC", value)
    value = _strip_zero_width(value)
    value = value.strip()

    _reject_control_chars(value, allow_tabs_newlines=False)
    _enforce_ascii_only(value, field)
    if not USERNAME_RE.fullmatch(value):
        raise ValidationError(
            f"'{field}' may only contain letters, numbers, '-' or '_' and must start/end with a letter or digit."
        )
    _require_non_blank(value, field)
    _enforce_length(value, field, min_len, max_len)
    return value


def validate_display_text(
    value: Optional[str],
    field: str = "display_name",
    *,
    required: bool = True,
    min_len: int = 3,
    max_len: int = 64,
) -> Optional[str]:
    """
    English-only single-line display strings.
    - Collapses extra spaces
    - Removes zero-width
    - Rejects controls and non-ASCII
    """
    if value is None:
        if required:
            raise ValidationError(f"'{field}' is required.")
        return None
    if not isinstance(value, str):
        raise ValidationError(f"'{field}' must be a string.")

    value = unicodedata.normalize("NFKC", value)
    value = _strip_zero_width(value)
    value = " ".join(value.split())  # collapse whitespace
    _reject_control_chars(value, allow_tabs_newlines=False)
    _enforce_ascii_only(value, field)
    _require_non_blank(value, field)
    _enforce_length(value, field, min_len, max_len)
    return value


def validate_multiline_text(
    value: Optional[str],
    field: str = "description",
    *,
    required: bool = False,
    min_len: int = 0,
    max_len: int = 4000,
) -> Optional[str]:
    """
    English-only multiline text (comments, descriptions).
    - Normalizes newlines
    - Strips zero-width and outer whitespace
    - Allows tabs/newlines, but no other control chars
    - Rejects non-ASCII
    """
    if value is None:
        if required:
            raise ValidationError(f"'{field}' is required.")
        return None
    if not isinstance(value, str):
        raise ValidationError(f"'{field}' must be a string.")

    value = unicodedata.normalize("NFKC", value)
    value = _strip_zero_width(value)
    value = value.replace("\r\n", "\n").replace("\r", "\n").strip()

    _reject_control_chars(value, allow_tabs_newlines=True)
    _enforce_ascii_only(value, field)
    _enforce_length(value, field, min_len, max_len)
    return value
