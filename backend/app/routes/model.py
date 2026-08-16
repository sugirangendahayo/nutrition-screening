from flask import Blueprint

from app.ml.feature_schema import get_schema_payload
from app.ml.provider_factory import get_provider, get_provider_error
from app.utils.auth import ROLE_ADMIN, ROLE_RESEARCHER, require_auth, require_role
from app.utils.responses import fail, ok

bp = Blueprint("model", __name__, url_prefix="/api/model")


@bp.get("/info")
@require_auth
def model_info():
    provider = get_provider()
    schema = get_schema_payload()

    if provider is None:
        return ok(
            {
                "available": False,
                "error": get_provider_error()
                or "No model provider is currently configured.",
                "schema": schema,
            }
        )

    payload = provider.describe()
    payload["available"] = True
    payload["schema"] = schema
    return ok(payload)


@bp.get("/performance")
@require_role(ROLE_ADMIN, ROLE_RESEARCHER)
def model_performance():
    """Surfaces stored evaluation metrics for trained model versions.

    Metrics are populated once a model has actually been trained and
    evaluated offline (accuracy, precision, recall, F1, ROC-AUC, confusion
    matrix per Chapter 3, Section 3.3.2). Until then this returns an empty
    list rather than inventing scores.
    """
    from app.services.supabase_service import get_supabase

    supabase = get_supabase()
    rows = (
        supabase.table("model_versions")
        .select("id, version, mode, targets, metrics, trained_at, is_active, created_at")
        .order("created_at", desc=True)
        .execute()
        .data
        or []
    )
    return ok({"versions": rows})
