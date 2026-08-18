"""Canonical definition of the nutrition-screening input features.

SOURCE OF TRUTH
----------------
This schema was built by directly inspecting the trained artifacts
(`backend/models/stunting_model.pkl`, `backend/models/underweight_model.pkl`)
and the training notebook (`docs/Child_Undernutrition_ML_Pipeline_FINAL_Colab_Statistical_ML_Joblib (1).ipynb`),
NOT invented. Both pipelines expect exactly these 20 raw MICS6 variable
codes, in this order, as `preprocessor.feature_names_in_`:

    CAGE, HL4, CA31, IM2, BD2, cdisability, cinsurance, melevel,
    caretakerdis, HH6, HH7, windex5, religion, ethnicity, CA1, CA14,
    CA16, CA17, TN3, EC1

CAGE is numeric (child age in months). All other 19 are categorical and
were one-hot encoded during training; the valid category codes below
(e.g. HL4 in {1.0, 2.0}) were read directly off the fitted
OneHotEncoder's learned categories (`preprocessor.get_feature_names_out()`)
- submitting any other value causes `handle_unknown="ignore"` to silently
zero out that feature, degrading the prediction.

IMPORTANT - LABEL CONFIDENCE
------------------------------
The MICS6 CAR codebook / SPSS value labels were not available at the time
this schema was written (the training notebook loads `ch_meta` from
`pyreadstat` but never prints its variable/value labels). Each field below
carries a `label_confidence`:

    "confirmed"           - taken directly from the notebook's own text
                             (e.g. CAGE is explicitly described as
                             "child age in months").
    "standard_convention" - not confirmed against the CAR codebook, but
                             follows the near-universal MICS/DHS naming
                             and coding convention for that variable
                             (e.g. HL4 = sex, 1=Male/2=Female; HH6 =
                             urban/rural; windex5 = wealth quintile).
    "unverified"           - meaning and/or category labels could not be
                             inferred responsibly and MUST be confirmed
                             against the actual MICS6 CAR codebook or the
                             dataset's embedded SPSS value labels before
                             this is treated as clinically reliable.

Fields marked "unverified" are shown to users with their raw code and a
visible notice rather than a guessed clinical label. See
docs/MODEL_INTEGRATION.md for the full findings and what is needed to
resolve them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class InputType(str, Enum):
    NUMBER = "number"
    SELECT = "select"
    RADIO = "radio"


class LabelConfidence(str, Enum):
    CONFIRMED = "confirmed"
    STANDARD_CONVENTION = "standard_convention"
    UNVERIFIED = "unverified"


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
    label_confidence: LabelConfidence
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
            "labelConfidence": self.label_confidence.value,
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

# Exact raw feature order expected by both trained pipelines. This MUST match
# `preprocessor.feature_names_in_` exactly - verified by direct inspection.
RAW_FEATURE_ORDER = [
    "CAGE", "HL4", "CA31", "IM2", "BD2", "cdisability", "cinsurance",
    "melevel", "caretakerdis", "HH6", "HH7", "windex5", "religion",
    "ethnicity", "CA1", "CA14", "CA16", "CA17", "TN3", "EC1",
]


def _code_options(values: list[str], names: dict[str, str] | None = None) -> tuple[FieldOption, ...]:
    """Build options from raw numeric codes. `names` optionally supplies a
    human label for specific codes when known; codes without a supplied
    name fall back to "Code <value>" so nothing is fabricated."""
    names = names or {}
    return tuple(FieldOption(v, names.get(v, f"Code {v}")) for v in values)


FEATURE_FIELDS: tuple[FeatureField, ...] = (
    # --- Child information --------------------------------------------
    FeatureField(
        key="CAGE",
        label="Child age",
        section="child_information",
        input_type=InputType.NUMBER,
        label_confidence=LabelConfidence.CONFIRMED,
        unit="months",
        min=0,
        max=59,
        step=1,
        help_text="Age in completed months. Confirmed from the training notebook.",
    ),
    FeatureField(
        key="HL4",
        label="Sex",
        section="child_information",
        input_type=InputType.SELECT,
        label_confidence=LabelConfidence.STANDARD_CONVENTION,
        options=_code_options(["1.0", "2.0"], {"1.0": "Male", "2.0": "Female"}),
        help_text="Standard MICS6 household-listing convention (HL4). Verify against the CAR codebook before clinical use.",
    ),
    FeatureField(
        key="cdisability",
        label="Child has a functional disability",
        section="child_information",
        input_type=InputType.RADIO,
        label_confidence=LabelConfidence.STANDARD_CONVENTION,
        options=_code_options(["1.0", "2.0"], {"1.0": "Yes", "2.0": "No"}),
        help_text="Variable name suggests child functional disability status. Verify wording/category order against the codebook.",
    ),
    FeatureField(
        key="cinsurance",
        label="Child covered by health insurance",
        section="child_information",
        input_type=InputType.RADIO,
        label_confidence=LabelConfidence.STANDARD_CONVENTION,
        options=_code_options(["1.0", "2.0"], {"1.0": "Yes", "2.0": "No"}),
        help_text="Verify against the codebook before clinical use.",
    ),
    FeatureField(
        key="CA31",
        label="CA31 (child care indicator - meaning pending verification)",
        section="child_information",
        input_type=InputType.SELECT,
        label_confidence=LabelConfidence.UNVERIFIED,
        options=_code_options(["1.0", "2.0", "3.0", "4.0", "5.0", "6.0", "96.0"]),
        help_text="Raw MICS6 code CA31. Meaning and category labels are not yet confirmed against the CAR codebook.",
    ),
    FeatureField(
        key="CA1",
        label="CA1 (child care indicator - meaning pending verification)",
        section="child_information",
        input_type=InputType.SELECT,
        label_confidence=LabelConfidence.UNVERIFIED,
        options=_code_options(["1.0", "2.0"]),
        help_text="Raw MICS6 code CA1. Meaning pending verification against the CAR codebook.",
    ),
    FeatureField(
        key="CA14",
        label="CA14 (child care indicator - meaning pending verification)",
        section="child_information",
        input_type=InputType.SELECT,
        label_confidence=LabelConfidence.UNVERIFIED,
        options=_code_options(["1.0", "2.0"]),
        help_text="Raw MICS6 code CA14. Meaning pending verification against the CAR codebook.",
    ),
    FeatureField(
        key="CA16",
        label="CA16 (child care indicator - meaning pending verification)",
        section="child_information",
        input_type=InputType.SELECT,
        label_confidence=LabelConfidence.UNVERIFIED,
        options=_code_options(["1.0", "2.0"]),
        help_text="Raw MICS6 code CA16. Meaning pending verification against the CAR codebook.",
    ),
    FeatureField(
        key="CA17",
        label="CA17 (child care indicator - meaning pending verification)",
        section="child_information",
        input_type=InputType.SELECT,
        label_confidence=LabelConfidence.UNVERIFIED,
        options=_code_options(["1.0", "2.0"]),
        help_text="Raw MICS6 code CA17. Meaning pending verification against the CAR codebook.",
    ),
    FeatureField(
        key="IM2",
        label="IM2 (immunization indicator - meaning pending verification)",
        section="health_environment",
        input_type=InputType.SELECT,
        label_confidence=LabelConfidence.UNVERIFIED,
        options=_code_options(["1.0", "2.0", "3.0", "4.0"]),
        help_text="Raw MICS6 immunization-module code IM2. Meaning pending verification against the CAR codebook.",
    ),
    FeatureField(
        key="BD2",
        label="BD2 (birth/development indicator - meaning pending verification)",
        section="child_information",
        input_type=InputType.RADIO,
        label_confidence=LabelConfidence.UNVERIFIED,
        options=_code_options(["1.0", "2.0"]),
        help_text="Raw MICS6 code BD2. Meaning pending verification against the CAR codebook.",
    ),
    FeatureField(
        key="TN3",
        label="TN3 (mosquito net indicator - meaning pending verification)",
        section="health_environment",
        input_type=InputType.RADIO,
        label_confidence=LabelConfidence.UNVERIFIED,
        options=_code_options(["1.0", "2.0"]),
        help_text="Raw MICS6 treated-nets-module code TN3. Meaning pending verification against the CAR codebook.",
    ),
    FeatureField(
        key="EC1",
        label="EC1 (early childhood indicator - meaning pending verification)",
        section="child_information",
        input_type=InputType.SELECT,
        label_confidence=LabelConfidence.UNVERIFIED,
        options=_code_options(["0.0", "1.0", "2.0", "3.0", "4.0", "5.0", "6.0", "7.0", "10.0"]),
        help_text="Raw MICS6 early-childhood-module code EC1. Meaning pending verification against the CAR codebook.",
    ),
    # --- Maternal / caretaker information ------------------------------
    FeatureField(
        key="melevel",
        label="Mother's/caretaker's education level",
        section="maternal_information",
        input_type=InputType.SELECT,
        label_confidence=LabelConfidence.STANDARD_CONVENTION,
        options=_code_options(
            ["0.0", "1.0", "2.0", "3.0"],
            {"0.0": "None", "1.0": "Primary", "2.0": "Secondary", "3.0": "Higher"},
        ),
        help_text="Standard MICS 'melevel' recode convention. Verify exact CAR category boundaries against the codebook.",
    ),
    FeatureField(
        key="caretakerdis",
        label="Caretaker has a functional disability",
        section="maternal_information",
        input_type=InputType.RADIO,
        label_confidence=LabelConfidence.STANDARD_CONVENTION,
        options=_code_options(["1.0", "2.0"], {"1.0": "Yes", "2.0": "No"}),
        help_text="Verify against the codebook before clinical use.",
    ),
    # --- Household information -----------------------------------------
    FeatureField(
        key="HH6",
        label="Area",
        section="household_information",
        input_type=InputType.SELECT,
        label_confidence=LabelConfidence.STANDARD_CONVENTION,
        options=_code_options(["1.0", "2.0"], {"1.0": "Urban", "2.0": "Rural"}),
        help_text="Standard MICS6 household module convention (HH6).",
    ),
    FeatureField(
        key="HH7",
        label="Region",
        section="household_information",
        input_type=InputType.SELECT,
        label_confidence=LabelConfidence.UNVERIFIED,
        options=_code_options(["1.0", "2.0", "3.0", "4.0", "5.0", "6.0", "7.0"]),
        help_text="CAR administrative region (HH7). Region names per code are not yet confirmed against the CAR codebook.",
    ),
    FeatureField(
        key="windex5",
        label="Household wealth quintile",
        section="household_information",
        input_type=InputType.SELECT,
        label_confidence=LabelConfidence.STANDARD_CONVENTION,
        options=_code_options(
            ["1.0", "2.0", "3.0", "4.0", "5.0"],
            {"1.0": "Poorest", "2.0": "Poorer", "3.0": "Middle", "4.0": "Richer", "5.0": "Richest"},
        ),
        help_text="Standard MICS/DHS wealth index quintile convention (windex5).",
    ),
    FeatureField(
        key="religion",
        label="Household religion",
        section="household_information",
        input_type=InputType.SELECT,
        label_confidence=LabelConfidence.UNVERIFIED,
        options=_code_options(["1.0", "2.0", "3.0", "4.0", "6.0", "7.0"]),
        help_text="CAR-specific religion categories are not yet confirmed against the codebook.",
    ),
    FeatureField(
        key="ethnicity",
        label="Household ethnicity",
        section="household_information",
        input_type=InputType.SELECT,
        label_confidence=LabelConfidence.UNVERIFIED,
        options=_code_options(["1.0", "2.0", "3.0", "4.0", "5.0", "6.0", "7.0", "96.0"]),
        help_text="CAR-specific ethnic group categories are not yet confirmed against the codebook.",
    ),
)


def get_fields_by_key() -> dict[str, FeatureField]:
    return {f.key: f for f in FEATURE_FIELDS}


# The `children` table stores sex as a dedicated Postgres enum
# (`child_sex`: 'male' | 'female') rather than the raw HL4 code, since it is
# a property of the child record itself (shared across all of that child's
# assessments), not a per-assessment prediction input. HL4's 1.0/2.0 ->
# male/female mapping is the same "standard_convention" assumption already
# documented on the HL4 field above and in docs/MODEL_INTEGRATION.md.
HL4_TO_CHILD_SEX = {"1.0": "male", "2.0": "female"}


def derive_child_sex(cleaned_input: dict) -> str | None:
    """Map the validated HL4 value to the `children.sex` enum, if present."""
    value = cleaned_input.get("HL4")
    if value is None:
        return None
    return HL4_TO_CHILD_SEX.get(str(value))


def get_schema_payload() -> dict:
    """Serializable schema consumed by the frontend to render the form."""
    return {
        "sections": SECTIONS,
        "fields": [f.to_dict() for f in FEATURE_FIELDS],
        "targets": PREDICTION_TARGETS,
    }
