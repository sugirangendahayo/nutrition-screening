import pytest

from app.utils.validation import ValidationError, validate_screening_input
from tests.conftest import VALID_SCREENING_INPUT


def test_valid_payload_passes():
    cleaned = validate_screening_input(VALID_SCREENING_INPUT)
    assert cleaned["child_age_months"] == 24
    assert cleaned["sex"] == "male"


def test_missing_required_field_is_rejected():
    payload = dict(VALID_SCREENING_INPUT)
    del payload["weight_kg"]
    with pytest.raises(ValidationError) as exc_info:
        validate_screening_input(payload)
    assert "weight_kg" in exc_info.value.errors


def test_out_of_range_number_is_rejected():
    payload = dict(VALID_SCREENING_INPUT)
    payload["child_age_months"] = 200
    with pytest.raises(ValidationError) as exc_info:
        validate_screening_input(payload)
    assert "child_age_months" in exc_info.value.errors


def test_non_numeric_value_is_rejected():
    payload = dict(VALID_SCREENING_INPUT)
    payload["weight_kg"] = "not-a-number"
    with pytest.raises(ValidationError) as exc_info:
        validate_screening_input(payload)
    assert "weight_kg" in exc_info.value.errors


def test_invalid_choice_is_rejected():
    payload = dict(VALID_SCREENING_INPUT)
    payload["sex"] = "unknown"
    with pytest.raises(ValidationError) as exc_info:
        validate_screening_input(payload)
    assert "sex" in exc_info.value.errors


def test_optional_field_can_be_omitted():
    payload = dict(VALID_SCREENING_INPUT)
    cleaned = validate_screening_input(payload)
    assert "muac_cm" not in cleaned
