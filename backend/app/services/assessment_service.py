"""Persistence and retrieval logic for children, assessments, and results.

Schema (see supabase/migrations/0001_init.sql):
    children                -> one row per child (de-identified: no name is stored)
    model_versions           -> one row per distinct model version/mode seen
    assessments               -> one row per nutrition screening event
    assessment_predictions    -> one row per (assessment, target)
    prediction_explanations   -> one row per (assessment, target, feature)
"""
from __future__ import annotations

from app.ml.types import PredictionBundle


def ensure_model_version(supabase, bundle: PredictionBundle) -> str:
    existing = (
        supabase.table("model_versions")
        .select("id")
        .eq("version", bundle.model_version)
        .eq("mode", bundle.mode)
        .limit(1)
        .execute()
    )
    if existing.data:
        return existing.data[0]["id"]

    inserted = (
        supabase.table("model_versions")
        .insert(
            {
                "version": bundle.model_version,
                "mode": bundle.mode,
                "targets": [t.target for t in bundle.targets],
            }
        )
        .execute()
    )
    return inserted.data[0]["id"]


def create_child(supabase, created_by: str, sex: str) -> dict:
    inserted = (
        supabase.table("children")
        .insert({"created_by": created_by, "sex": sex})
        .execute()
    )
    return inserted.data[0]


def get_child(supabase, child_id: str) -> dict | None:
    result = supabase.table("children").select("*").eq("id", child_id).limit(1).execute()
    return result.data[0] if result.data else None


def find_child_by_code(supabase, child_code: str) -> dict | None:
    result = (
        supabase.table("children")
        .select("*")
        .eq("child_code", child_code)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def list_children(supabase, search: str | None = None, limit: int = 50) -> list[dict]:
    query = supabase.table("children").select("*").order("created_at", desc=True).limit(limit)
    if search:
        query = query.ilike("child_code", f"%{search}%")
    return query.execute().data or []


def create_assessment(
    supabase,
    *,
    child_id: str,
    performed_by: str,
    input_data: dict,
    bundle: PredictionBundle,
    notes: str | None = None,
) -> str:
    model_version_id = ensure_model_version(supabase, bundle)

    assessment = (
        supabase.table("assessments")
        .insert(
            {
                "child_id": child_id,
                "performed_by": performed_by,
                "model_version_id": model_version_id,
                "input_data": input_data,
                "notes": notes,
            }
        )
        .execute()
    ).data[0]

    assessment_id = assessment["id"]

    prediction_rows = [
        {
            "assessment_id": assessment_id,
            "target": t.target,
            "predicted_label": t.predicted_label,
            "probability": t.probability,
        }
        for t in bundle.targets
    ]
    supabase.table("assessment_predictions").insert(prediction_rows).execute()

    explanation_rows = []
    for explanation in bundle.explanations:
        for rank, item in enumerate(explanation.items, start=1):
            explanation_rows.append(
                {
                    "assessment_id": assessment_id,
                    "target": explanation.target,
                    "method": explanation.method,
                    "feature_key": item.feature_key,
                    "feature_label": item.feature_label,
                    "contribution": item.contribution,
                    "direction": item.direction,
                    "rank": rank,
                }
            )
    if explanation_rows:
        supabase.table("prediction_explanations").insert(explanation_rows).execute()

    return assessment_id


def _shape_predictions(rows: list[dict]) -> dict:
    return {
        row["target"]: {
            "predictedLabel": row["predicted_label"],
            "probability": row["probability"],
        }
        for row in rows
    }


def _shape_explanations(rows: list[dict]) -> list[dict]:
    grouped: dict[str, dict] = {}
    for row in rows:
        target = row["target"]
        bucket = grouped.setdefault(
            target, {"target": target, "method": row["method"], "items": []}
        )
        bucket["items"].append(
            {
                "featureKey": row["feature_key"],
                "featureLabel": row["feature_label"],
                "contribution": row["contribution"],
                "direction": row["direction"],
            }
        )
    for bucket in grouped.values():
        bucket["items"].sort(key=lambda i: abs(i["contribution"]), reverse=True)
    return list(grouped.values())


def get_assessment_detail(supabase, assessment_id: str) -> dict | None:
    result = (
        supabase.table("assessments")
        .select(
            "id, child_id, performed_by, input_data, notes, assessed_at, "
            "children(id, child_code, sex), "
            "model_versions(version, mode), "
            "profiles(full_name), "
            "assessment_predictions(target, predicted_label, probability), "
            "prediction_explanations(target, method, feature_key, feature_label, contribution, direction)"
        )
        .eq("id", assessment_id)
        .limit(1)
        .execute()
    )
    if not result.data:
        return None

    row = result.data[0]
    return {
        "id": row["id"],
        "child": row["children"],
        "performedBy": row["performed_by"],
        "performedByName": row["profiles"]["full_name"] if row.get("profiles") else None,
        "inputData": row["input_data"],
        "notes": row["notes"],
        "assessedAt": row["assessed_at"],
        "modelVersion": row["model_versions"]["version"] if row["model_versions"] else None,
        "mode": row["model_versions"]["mode"] if row["model_versions"] else None,
        "predictions": _shape_predictions(row["assessment_predictions"]),
        "explanations": _shape_explanations(row["prediction_explanations"]),
    }


def list_assessments(
    supabase,
    *,
    performed_by: str | None = None,
    child_id: str | None = None,
    limit: int = 50,
) -> list[dict]:
    query = (
        supabase.table("assessments")
        .select(
            "id, child_id, performed_by, assessed_at, "
            "children(child_code, sex), "
            "assessment_predictions(target, predicted_label, probability)"
        )
        .order("assessed_at", desc=True)
        .limit(limit)
    )
    if performed_by:
        query = query.eq("performed_by", performed_by)
    if child_id:
        query = query.eq("child_id", child_id)

    rows = query.execute().data or []
    return [
        {
            "id": row["id"],
            "childId": row["child_id"],
            "childCode": row["children"]["child_code"] if row["children"] else None,
            "sex": row["children"]["sex"] if row["children"] else None,
            "performedBy": row["performed_by"],
            "assessedAt": row["assessed_at"],
            "predictions": _shape_predictions(row["assessment_predictions"]),
        }
        for row in rows
    ]


def get_child_history(supabase, child_id: str) -> list[dict]:
    rows = (
        supabase.table("assessments")
        .select("id, assessed_at, assessment_predictions(target, predicted_label, probability)")
        .eq("child_id", child_id)
        .order("assessed_at", desc=False)
        .execute()
        .data
        or []
    )
    return [
        {
            "id": row["id"],
            "assessedAt": row["assessed_at"],
            "predictions": _shape_predictions(row["assessment_predictions"]),
        }
        for row in rows
    ]
