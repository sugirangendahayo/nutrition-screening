"""Report content assembly. Report rendering/printing happens on the
frontend (print-optimized view); this service is responsible for
gathering the underlying data and logging that a report was generated.
"""
from __future__ import annotations

from app.ml.feature_schema import PREDICTION_TARGETS, get_fields_by_key
from app.services import assessment_service
from app.services.trend_service import compute_trend


def build_assessment_report(supabase, assessment_id: str) -> dict | None:
    detail = assessment_service.get_assessment_detail(supabase, assessment_id)
    if not detail:
        return None

    fields_by_key = get_fields_by_key()
    input_summary = [
        {
            "label": fields_by_key[key].label,
            "value": value,
            "unit": fields_by_key[key].unit,
        }
        for key, value in detail["inputData"].items()
        if key in fields_by_key
    ]

    history = assessment_service.get_child_history(supabase, detail["child"]["id"])
    trend = compute_trend(history, PREDICTION_TARGETS)

    return {
        "assessment": detail,
        "inputSummary": input_summary,
        "trend": trend,
    }


def log_report(supabase, *, assessment_id: str | None, child_id: str | None, generated_by: str, report_type: str = "assessment_summary"):
    supabase.table("reports").insert(
        {
            "assessment_id": assessment_id,
            "child_id": child_id,
            "generated_by": generated_by,
            "report_type": report_type,
        }
    ).execute()


def list_reports(supabase, *, generated_by: str | None = None, limit: int = 50) -> list[dict]:
    query = (
        supabase.table("reports")
        .select(
            "id, assessment_id, child_id, report_type, created_at, "
            "children(child_code), assessments(assessed_at)"
        )
        .order("created_at", desc=True)
        .limit(limit)
    )
    if generated_by:
        query = query.eq("generated_by", generated_by)

    rows = query.execute().data or []
    return [
        {
            "id": row["id"],
            "assessmentId": row["assessment_id"],
            "childCode": row["children"]["child_code"] if row.get("children") else None,
            "assessedAt": row["assessments"]["assessed_at"] if row.get("assessments") else None,
            "reportType": row["report_type"],
            "createdAt": row["created_at"],
        }
        for row in rows
    ]
