"""Aggregate statistics for the dashboard. Every number is derived from
real stored data - if there is no data yet, callers should render an
explicit "No data yet" state rather than a fabricated number."""
from __future__ import annotations

from datetime import datetime, timezone


def _month_start_iso() -> str:
    now = datetime.now(timezone.utc)
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()


def get_dashboard_summary(supabase) -> dict:
    children_count = (
        supabase.table("children").select("id", count="exact").execute().count or 0
    )

    month_start = _month_start_iso()
    assessments_this_month = (
        supabase.table("assessments")
        .select("id", count="exact")
        .gte("assessed_at", month_start)
        .execute()
        .count
        or 0
    )

    predictions_this_month = (
        supabase.table("assessment_predictions")
        .select("target, predicted_label, assessments!inner(assessed_at)")
        .gte("assessments.assessed_at", month_start)
        .execute()
        .data
        or []
    )

    stunting_at_risk = sum(
        1
        for row in predictions_this_month
        if row["target"] == "stunting" and row["predicted_label"] == "at_risk"
    )
    underweight_at_risk = sum(
        1
        for row in predictions_this_month
        if row["target"] == "underweight" and row["predicted_label"] == "at_risk"
    )

    recent = (
        supabase.table("assessments")
        .select(
            "id, assessed_at, children(child_code), assessment_predictions(target, predicted_label, probability)"
        )
        .order("assessed_at", desc=True)
        .limit(5)
        .execute()
        .data
        or []
    )
    recent_predictions = [
        {
            "id": row["id"],
            "childCode": row["children"]["child_code"] if row["children"] else None,
            "assessedAt": row["assessed_at"],
            "predictions": {
                p["target"]: {"predictedLabel": p["predicted_label"], "probability": p["probability"]}
                for p in row["assessment_predictions"]
            },
        }
        for row in recent
    ]

    return {
        "childrenAssessed": children_count,
        "assessmentsThisMonth": assessments_this_month,
        "stuntingAtRiskThisMonth": stunting_at_risk,
        "underweightAtRiskThisMonth": underweight_at_risk,
        "recentAssessments": recent_predictions,
        "hasData": children_count > 0,
    }
