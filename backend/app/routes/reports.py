from flask import Blueprint, g, request

from app.services import report_service
from app.services.supabase_service import get_supabase
from app.utils.auth import (
    ROLE_ADMIN,
    ROLE_HEALTHCARE_WORKER,
    ROLE_NUTRITION_OFFICER,
    require_auth,
    require_role,
)
from app.utils.responses import fail, ok

bp = Blueprint("reports", __name__, url_prefix="/api/reports")


@bp.get("")
@require_auth
def list_reports_route():
    supabase = get_supabase()
    mine_only = request.args.get("mine") == "true"
    generated_by = g.current_user["id"] if mine_only else None
    rows = report_service.list_reports(supabase, generated_by=generated_by)
    return ok({"reports": rows})


@bp.get("/assessment/<assessment_id>")
@require_auth
def get_report(assessment_id: str):
    supabase = get_supabase()
    report = report_service.build_assessment_report(supabase, assessment_id)
    if not report:
        return fail("Assessment not found.", status=404)
    return ok(report)


@bp.post("")
@require_role(ROLE_ADMIN, ROLE_HEALTHCARE_WORKER, ROLE_NUTRITION_OFFICER)
def create_report():
    payload = request.get_json(silent=True) or {}
    assessment_id = payload.get("assessmentId")
    if not assessment_id:
        return fail("assessmentId is required.", status=422)

    supabase = get_supabase()
    report = report_service.build_assessment_report(supabase, assessment_id)
    if not report:
        return fail("Assessment not found.", status=404)

    report_service.log_report(
        supabase,
        assessment_id=assessment_id,
        child_id=report["assessment"]["child"]["id"],
        generated_by=g.current_user["id"],
    )
    return ok(report, status=201)
