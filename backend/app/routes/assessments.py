"""Persisted nutrition screening assessments.

Predictions stored here are always recomputed server-side from the
submitted input data (never trusted from the client) to guarantee the
saved result always reflects the actual model output for that input.
"""
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
    require_auth,
    require_role,
)
from app.utils.responses import fail, ok
from app.utils.validation import ValidationError, validate_screening_input

bp = Blueprint("assessments", __name__, url_prefix="/api/assessments")


@bp.post("")
@require_role(ROLE_ADMIN, ROLE_HEALTHCARE_WORKER, ROLE_NUTRITION_OFFICER)
def create_assessment():
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
    notes = payload.get("notes")

    try:
        cleaned = validate_screening_input(features)
    except ValidationError as exc:
        return fail("Please correct the highlighted fields.", status=422, details=exc.errors)

    supabase = get_supabase()

    if child_id:
        child = assessment_service.get_child(supabase, child_id)
        if not child:
            return fail("The selected child record could not be found.", status=404)
    else:
        if "sex" not in cleaned:
            return fail("Sex is required to create a new child record.", status=422)
        child = assessment_service.create_child(
            supabase, created_by=g.current_user["id"], sex=cleaned["sex"]
        )

    bundle = provider.predict(cleaned)

    assessment_id = assessment_service.create_assessment(
        supabase,
        child_id=child["id"],
        performed_by=g.current_user["id"],
        input_data=cleaned,
        bundle=bundle,
        notes=notes,
    )

    detail = assessment_service.get_assessment_detail(supabase, assessment_id)
    history = assessment_service.get_child_history(supabase, child["id"])
    detail["trend"] = compute_trend(history, PREDICTION_TARGETS)
    return ok(detail, status=201)


@bp.get("")
@require_auth
def list_assessments():
    supabase = get_supabase()
    child_id = request.args.get("childId")
    mine_only = request.args.get("mine") == "true"

    performed_by = g.current_user["id"] if mine_only else None
    rows = assessment_service.list_assessments(
        supabase, performed_by=performed_by, child_id=child_id
    )
    return ok({"assessments": rows})


@bp.get("/<assessment_id>")
@require_auth
def get_assessment(assessment_id: str):
    supabase = get_supabase()
    detail = assessment_service.get_assessment_detail(supabase, assessment_id)
    if not detail:
        return fail("Assessment not found.", status=404)

    history = assessment_service.get_child_history(supabase, detail["child"]["id"])
    detail["trend"] = compute_trend(history, PREDICTION_TARGETS)
    return ok(detail)
