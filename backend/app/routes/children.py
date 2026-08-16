from flask import Blueprint, request

from app.ml.feature_schema import PREDICTION_TARGETS
from app.services import assessment_service
from app.services.supabase_service import get_supabase
from app.services.trend_service import compute_trend
from app.utils.auth import require_auth
from app.utils.responses import fail, ok

bp = Blueprint("children", __name__, url_prefix="/api/children")


@bp.get("")
@require_auth
def list_children():
    supabase = get_supabase()
    search = request.args.get("search")
    rows = assessment_service.list_children(supabase, search=search)
    return ok({"children": rows})


@bp.get("/<child_id>")
@require_auth
def get_child(child_id: str):
    supabase = get_supabase()
    child = assessment_service.get_child(supabase, child_id)
    if not child:
        return fail("Child record not found.", status=404)
    return ok(child)


@bp.get("/<child_id>/history")
@require_auth
def get_child_history(child_id: str):
    supabase = get_supabase()
    child = assessment_service.get_child(supabase, child_id)
    if not child:
        return fail("Child record not found.", status=404)

    assessments = assessment_service.list_assessments(supabase, child_id=child_id)
    history = assessment_service.get_child_history(supabase, child_id)
    trend = compute_trend(history, PREDICTION_TARGETS)

    return ok({"child": child, "assessments": assessments, "trend": trend})
