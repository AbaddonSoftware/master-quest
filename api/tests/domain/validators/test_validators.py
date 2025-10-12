import types
import pytest
from flask import Flask, g
from werkzeug.exceptions import HTTPException

from domain.validators import (
    validate_int_field,
    validate_string_field,
    validate_string_length,
)
from domain.validators.validators import _require_field

# ---------- Helpers / Fixtures ----------


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config.update(SECRET_KEY="test")
    return app


@pytest.fixture
def req_ctx(app):
    with app.test_request_context("/"):
        yield


# ---------- _require_field ----------


def test_require_field_aborts_400_on_None():
    with pytest.raises(HTTPException) as e:
        _require_field(None, "field_name")
    assert e.value.code == 400


def test_require_field_allows_zero():
    result = _require_field(0, "field_name")
    assert result == None


def test_require_field_allows_false():
    result = _require_field(False, "field_name")
    assert result == None


# ---------- validate_string_field ----------


def test_validate_string_field_required_none_aborts():
    with pytest.raises(HTTPException) as e:
        validate_string_field(None, "field_name", required=True)
    assert e.value.code == 400


def test_validate_string_field_returns_string_on_success():
    result = validate_string_field("Field", "field_name", required=True)
    assert result == "Field"


def test_validate_string_field_optional_none_returns_none():
    result = validate_string_field(None, "field_name", required=False)
    assert result == None

def test_validate_string_field_option_empty_aborts():
    with pytest.raises(HTTPException) as e:
        validate_string_field("", "field_name", required=False)
    assert e.value.code == 400


def test_validate_string_field_returns_stripped_on_success():
    result = validate_string_field(" Field  ", "field_name")
    assert result == "Field"


# ---------- validate_int_field ----------


def test_validate_int_field_required_none_aborts():
    with pytest.raises(HTTPException) as e:
        validate_int_field(None, "field_name", required=True)
    assert e.value.code == 400


def test_validate_int_field_required_returns_value_on_success():
    result = validate_int_field(42, "field_name", required=True)
    assert result == 42


def test_validate_int_field_optional_none_returns_none():
    result = validate_int_field(None, "field_name", required=False)
    assert result == None


def test_validate_int_field_optional_int_returns_int():
    result = validate_int_field(5, "field_name", required=False)
    assert result == 5


# ---------- get_authenticated_user_id ----------


def test_get_authenticated_user_id_returns_id(req_ctx):
    g.user = types.SimpleNamespace(id=7, name="Alice")
    from api.src.domain.validators import (  # re-import inside context
        get_authenticated_user_id,
    )
    result = get_authenticated_user_id()
    assert result == 7


# # ---------- validate_string_length ----------


def test_validate_string_length_within_bounds_passes():
    result = validate_string_length("field", 1, 10, "field_name")
    assert result is "field"


def test_validate_string_length_too_short_aborts():
    with pytest.raises(HTTPException) as e:
        validate_string_length("fi", 3, 10, "field_name")
    assert e.value.code == 400


def test_validate_string_length_too_long_aborts():
    with pytest.raises(HTTPException) as e:
        validate_string_length("x" * 11, 1, 10, "field_name")
    assert e.value.code == 400
