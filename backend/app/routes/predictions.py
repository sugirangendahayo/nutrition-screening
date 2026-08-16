"""Ephemeral prediction endpoint: run the model and return a result the
user can review, WITHOUT persisting anything. Saving happens separately
via POST /api/assessments once the user confirms the result."""
from flask import Blueprint, g, request

from app.ml.feature_schema import PREDICTION_TARGETS
from app.ml.provider_factory import get_provider, get_provider_error
from app.services import assessment_service
from app.services.supabase_service import get_supabase
from app.services.trend_service import compute_trend
from app.utils.auth import (
    ROLE_ADMIN,
    ROLE_HEALTHCARE_WORKER,
    ROLE_NUTRITION_OFFICER,
    require_role,
)
from app.utils.responses import fail, ok
from app.utils.validation import ValidationError, validate_screening_input

bp = Blueprint("predictions", __name__, url_prefix="/api/predictions")


@bp.post("")
@require_role(ROLE_ADMIN, ROLE_HEALTHCARE_WORKER, ROLE_NUTRITION_OFFICER)
def run_prediction():
    provider = get_provider()
    if provider is None:
        return fail(
            get_provider_error()
            or "No prediction model is currently available. Contact an administrator.",
            status=503,
        )

    payload = request.get_json(silent=True) or {}
    features = payload.get("inputData", {})
    child_id = payload.get("childId")

    try:
        cleaned = validate_screening_input(features)
    except ValidationError as exc:
        return fail("Please correct the highlighted fields.", status=422, details=exc.errors)

    bundle = provider.predict(cleaned)
    response = bundle.to_dict()
    response["inputData"] = cleaned

    if child_id:
        supabase = get_supabase()
        child = assessment_service.get_child(supabase, child_id)
        if child:
            history = assessment_service.get_child_history(supabase, child_id)
            preview_history = history + [
                {
                    "assessedAt": bundle.generated_at,
                    "predictions": {t.target: t.to_dict() for t in bundle.targets},
                }
            ]
            response["trendPreview"] = compute_trend(preview_history, PREDICTION_TARGETS)

    return ok(response)
