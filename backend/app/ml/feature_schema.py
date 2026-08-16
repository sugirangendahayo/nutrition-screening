"""Canonical definition of the nutrition-screening input features.

IMPORTANT
---------
This is the single source of truth for the fields collected on the
screening form. The frontend does NOT hard-code its own field list - it
fetches this schema from ``GET /api/model/info`` and renders the form
dynamically. This means that when the real trained model artifact
arrives, updating this file (to match the model's actual expected
features) is enough to keep the frontend and backend in sync without a
frontend rebuild.

The fields below are the CANDIDATE predictors identified in the research
(Chapter 3, Section 3.3.2) plus a small number of standard MICS6-style
anthropometric fields needed to run a nutrition screening at all
(weight, height, MUAC). They are placeholders for development and
testing only. When the trained `.pkl`/`.joblib` artifact is supplied it
MUST be inspected, and this schema must be updated to exactly match the
model's real expected feature names, order, and types before the system
is switched to production mode.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class InputType(str, Enum):
    NUMBER = "number"
    SELECT = "select"
    RADIO = "radio"


@dataclass(frozen=True)
class FieldOption:
    value: str
    label: str


@dataclass(frozen=True)
class FeatureField:
    key: str
    label: str
    section: str
    input_type: InputType
    required: bool = True
    unit: str | None = None
    min: float | None = None
    max: float | None = None
    step: float | None = None
    options: tuple[FieldOption, ...] = field(default_factory=tuple)
    help_text: str | None = None

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "label": self.label,
            "section": self.section,
            "inputType": self.input_type.value,
            "required": self.required,
            "unit": self.unit,
            "min": self.min,
            "max": self.max,
            "step": self.step,
            "options": [option.__dict__ for option in self.options],
            "helpText": self.help_text,
        }


SECTIONS = [
    {"key": "child_information", "label": "Child Information", "order": 1},
    {"key": "maternal_information", "label": "Maternal Information", "order": 2},
    {"key": "household_information", "label": "Household Information", "order": 3},
    {"key": "health_environment", "label": "Health & Environment", "order": 4},
]

PREDICTION_TARGETS = ["stunting", "underweight"]

FEATURE_FIELDS: tuple[FeatureField, ...] = (
    # --- Child information ------------------------------------------------
    FeatureField(
        key="child_age_months",
        label="Child age",
        section="child_information",
        input_type=InputType.NUMBER,
        unit="months",
        min=0,
        max=59,
        step=1,
        help_text="Age in completed months (0-59).",
    ),
    FeatureField(
        key="sex",
        label="Sex",
        section="child_information",
        input_type=InputType.SELECT,
        options=(FieldOption("male", "Male"), FieldOption("female", "Female")),
    ),
    FeatureField(
        key="weight_kg",
        label="Weight",
        section="child_information",
        input_type=InputType.NUMBER,
        unit="kg",
        min=1,
        max=30,
        step=0.1,
    ),
    FeatureField(
        key="height_cm",
        label="Height / length",
        section="child_information",
        input_type=InputType.NUMBER,
        unit="cm",
        min=30,
        max=150,
        step=0.1,
        help_text="Recumbent length if under 2 years, standing height otherwise.",
    ),
    FeatureField(
        key="muac_cm",
        label="Mid-upper arm circumference (MUAC)",
        section="child_information",
        input_type=InputType.NUMBER,
        unit="cm",
        required=False,
        min=5,
        max=25,
        step=0.1,
    ),
    FeatureField(
        key="birth_order",
        label="Birth order",
        section="child_information",
        input_type=InputType.NUMBER,
        required=False,
        min=1,
        max=20,
        step=1,
        help_text="Position of this child among all births to the mother.",
    ),
    FeatureField(
        key="breastfeeding_status",
        label="Breastfeeding status",
        section="child_information",
        input_type=InputType.SELECT,
        options=(
            FieldOption("currently_breastfeeding", "Currently breastfeeding"),
            FieldOption("no_longer_breastfeeding", "No longer breastfeeding"),
            FieldOption("never_breastfed", "Never breastfed"),
        ),
    ),
    # --- Maternal information ----------------------------------------------
    FeatureField(
        key="mother_education_level",
        label="Mother's education level",
        section="maternal_information",
        input_type=InputType.SELECT,
        options=(
            FieldOption("none", "None"),
            FieldOption("primary", "Primary"),
            FieldOption("secondary", "Secondary"),
            FieldOption("higher", "Higher"),
        ),
    ),
    FeatureField(
        key="mother_age_years",
        label="Mother's age",
        section="maternal_information",
        input_type=InputType.NUMBER,
        unit="years",
        required=False,
        min=12,
        max=60,
        step=1,
    ),
    FeatureField(
        key="antenatal_visits",
        label="Antenatal care visits during pregnancy",
        section="maternal_information",
        input_type=InputType.NUMBER,
        required=False,
        min=0,
        max=20,
        step=1,
    ),
    # --- Household information ----------------------------------------------
    FeatureField(
        key="household_wealth_index",
        label="Household wealth status",
        section="household_information",
        input_type=InputType.SELECT,
        options=(
            FieldOption("poorest", "Poorest"),
            FieldOption("poorer", "Poorer"),
            FieldOption("middle", "Middle"),
            FieldOption("richer", "Richer"),
            FieldOption("richest", "Richest"),
        ),
    ),
    FeatureField(
        key="residence_type",
        label="Residence type",
        section="household_information",
        input_type=InputType.SELECT,
        options=(FieldOption("urban", "Urban"), FieldOption("rural", "Rural")),
    ),
    FeatureField(
        key="household_size",
        label="Household size",
        section="household_information",
        input_type=InputType.NUMBER,
        required=False,
        min=1,
        max=30,
        step=1,
    ),
    FeatureField(
        key="children_under5_in_household",
        label="Children under 5 in household",
        section="household_information",
        input_type=InputType.NUMBER,
        required=False,
        min=1,
        max=15,
        step=1,
    ),
    # --- Health & environment ----------------------------------------------
    FeatureField(
        key="drinking_water_source",
        label="Drinking water source",
        section="health_environment",
        input_type=InputType.SELECT,
        options=(
            FieldOption("improved", "Improved source"),
            FieldOption("unimproved", "Unimproved source"),
        ),
    ),
    FeatureField(
        key="sanitation_facility",
        label="Sanitation facility",
        section="health_environment",
        input_type=InputType.SELECT,
        options=(
            FieldOption("improved", "Improved facility"),
            FieldOption("unimproved", "Unimproved facility"),
        ),
    ),
    FeatureField(
        key="vitamin_a_supplementation",
        label="Vitamin A supplementation (last 6 months)",
        section="health_environment",
        input_type=InputType.RADIO,
        options=(FieldOption("yes", "Yes"), FieldOption("no", "No")),
    ),
    FeatureField(
        key="immunization_status",
        label="Immunization status",
        section="health_environment",
        input_type=InputType.SELECT,
        options=(
            FieldOption("fully_immunized", "Fully immunized"),
            FieldOption("partially_immunized", "Partially immunized"),
            FieldOption("not_immunized", "Not immunized"),
        ),
    ),
    FeatureField(
        key="recent_diarrhea_episode",
        label="Diarrhea episode in the last 2 weeks",
        section="health_environment",
        input_type=InputType.RADIO,
        required=False,
        options=(FieldOption("yes", "Yes"), FieldOption("no", "No")),
    ),
)


def get_fields_by_key() -> dict[str, FeatureField]:
    return {f.key: f for f in FEATURE_FIELDS}


def get_schema_payload() -> dict:
    """Serializable schema consumed by the frontend to render the form."""
    return {
        "sections": SECTIONS,
        "fields": [f.to_dict() for f in FEATURE_FIELDS],
        "targets": PREDICTION_TARGETS,
    }
