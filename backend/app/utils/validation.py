"""Backend validation for nutrition-screening input.

This mirrors (and enforces server-side, never trusting the client) the
constraints defined in the canonical feature schema. Frontend validation
exists for UX only - this is the authoritative check.
"""
from __future__ import annotations

from app.ml.feature_schema import InputType, get_fields_by_key


class ValidationError(Exception):
    def __init__(self, errors: dict[str, str]):
        self.errors = errors
        super().__init__("Validation failed")


def _validate_number(field, raw_value):
    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        return None, f"Please enter a valid number for {field.label.lower()}."

    if field.min is not None and value < field.min:
        return None, f"{field.label} must be at least {field.min}{(' ' + field.unit) if field.unit else ''}."
    if field.max is not None and value > field.max:
        return None, f"{field.label} must be no more than {field.max}{(' ' + field.unit) if field.unit else ''}."
    return value, None


def _validate_choice(field, raw_value):
    valid_values = {opt.value for opt in field.options}
    if raw_value not in valid_values:
        return None, f"Please select a valid option for {field.label.lower()}."
    return raw_value, None


def validate_screening_input(payload: dict) -> dict:
    """Validate raw screening form input against the feature schema.

    Returns a cleaned dict of typed values keyed by feature key.
    Raises ValidationError with a dict of field -> message on failure.
    """
    if not isinstance(payload, dict):
        raise ValidationError({"_form": "Invalid request body."})

    fields_by_key = get_fields_by_key()
    errors: dict[str, str] = {}
    cleaned: dict = {}

    for key, field in fields_by_key.items():
        raw_value = payload.get(key, None)
        is_missing = raw_value is None or raw_value == ""

        if is_missing:
            if field.required:
                errors[key] = f"{field.label} is required."
            continue

        if field.input_type == InputType.NUMBER:
            value, error = _validate_number(field, raw_value)
        else:
            value, error = _validate_choice(field, raw_value)

        if error:
            errors[key] = error
        else:
            cleaned[key] = value

    # Unknown keys (e.g. client-side only helper fields) are ignored rather
    # than rejected, since they don't affect the model input.

    if errors:
        raise ValidationError(errors)

    return cleaned
