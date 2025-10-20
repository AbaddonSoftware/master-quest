import types

import pytest
from domain.exceptions import ValidationError
from domain.validators import validate_int, validate_str, validate_user_logged_in
from flask import Flask, g
from werkzeug.exceptions import HTTPException

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


# --- validate_str ---


def test_validate_str_return_string_on_success_required():
    result = validate_str("field", "field_name", required=True)
    assert result == "field"


def test_validate_str_return_string_on_success_optional():
    result = validate_str("a_valid_field", "field_name", required=False)
    assert result == "a_valid_field"


def test_validate_str_aborts_on_nonstring_if_required():
    with pytest.raises(ValidationError) as e:
        validate_str(0, "field_name", required=True)
    assert e.value.status_code == 422


def test_validate_str_passes_none_if_optional():
    result = validate_str(None, "field_name", required=False)
    assert result is None


def test_validate_str_strips_string_on_success_required():
    result = validate_str("  field   ", "field_name", required=True)
    assert result == "field"


def test_validate_str_strips_string_on_success_optional():
    result = validate_str("   field  ", "field_name", required=False)
    assert result == "field"


def test_validate_str_aborts_empty_string_required():
    with pytest.raises(ValidationError) as e:
        validate_str("", "field_name", required=True)
    assert e.value.status_code == 422


def test_validate_str_aborts_empty_string_optional():
    with pytest.raises(ValidationError) as e:
        validate_str("", "field_name", required=False)
    assert e.value.status_code == 422


def test_validate_str_aborts_onlyspace_string_required():
    with pytest.raises(ValidationError) as e:
        validate_str("      ", "field_name", required=True)
    assert e.value.status_code == 422


def test_validate_str_aborts_onlywhitespace_string_optional():
    with pytest.raises(ValidationError) as e:
        validate_str("      ", "field_name", required=False)
    assert e.value.status_code == 422


# --- validate_int ---


def test_validate_int_field_required_none_aborts():
    with pytest.raises(ValidationError) as e:
        validate_int(None, "field_name", required=True)
    assert e.value.status_code == 422


def test_validate_int_field_required_returns_value_on_success():
    result = validate_int(42, "field_name", required=True)
    assert result == 42


def test_validate_int_field_optional_none_returns_none():
    result = validate_int(None, "field_name", required=False)
    assert result == None


def test_validate_int_field_optional_int_returns_int():
    result = validate_int(5, "field_name", required=False)
    assert result == 5


# --- validate_user_logged_in ---


def test_validated_user_logged_in_returns_id(req_ctx):
    g.user = types.SimpleNamespace(id=7, name="Alice")
    from api.src.domain.validators import validate_user_logged_in

    result = validate_user_logged_in()
    assert result == 7
