import pytest

from app.utils.validation import ValidationError, validate_screening_input
from tests.conftest import VALID_SCREENING_INPUT


def test_valid_payload_passes():
    cleaned = validate_screening_input(VALID_SCREENING_INPUT)
    assert cleaned["CAGE"] == 24
    assert cleaned["HL4"] == "1.0"


def test_missing_required_field_is_rejected():
    payload = dict(VALID_SCREENING_INPUT)
    del payload["CAGE"]
    with pytest.raises(ValidationError) as exc_info:
        validate_screening_input(payload)
    assert "CAGE" in exc_info.value.errors


def test_out_of_range_number_is_rejected():
    payload = dict(VALID_SCREENING_INPUT)
    payload["CAGE"] = 200
    with pytest.raises(ValidationError) as exc_info:
        validate_screening_input(payload)
    assert "CAGE" in exc_info.value.errors


def test_non_numeric_value_is_rejected():
    payload = dict(VALID_SCREENING_INPUT)
    payload["CAGE"] = "not-a-number"
    with pytest.raises(ValidationError) as exc_info:
        validate_screening_input(payload)
    assert "CAGE" in exc_info.value.errors


def test_invalid_choice_is_rejected():
    payload = dict(VALID_SCREENING_INPUT)
    payload["HL4"] = "unknown-code"
    with pytest.raises(ValidationError) as exc_info:
        validate_screening_input(payload)
    assert "HL4" in exc_info.value.errors


def test_all_fields_are_required_in_current_schema():
    """Every one of the 20 model features is currently marked required,
    since the trained pipelines expect a complete raw record."""
    payload = dict(VALID_SCREENING_INPUT)
    del payload["windex5"]
    with pytest.raises(ValidationError) as exc_info:
        validate_screening_input(payload)
    assert "windex5" in exc_info.value.errors
