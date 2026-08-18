"""Application configuration loaded from environment variables.

A single source of truth for runtime configuration. Nothing here should
contain secrets by default - real values are supplied via a local `.env`
file (see `.env.example`) which is never committed to source control.
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
    PORT = int(os.environ.get("PORT", "5000"))

    CORS_ORIGINS = _split_csv(os.environ.get("CORS_ORIGINS", "http://localhost:5173"))

    # --- Supabase -----------------------------------------------------
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
    SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "")

    # --- ML model -------------------------------------------------------
    # "development" allows the app to run with the mock provider when no
    # trained artifact is available. "production" requires the two real
    # artifacts below to load successfully.
    ML_MODEL_STATUS = os.environ.get("ML_MODEL_STATUS", "production")

    STUNTING_MODEL_PATH = os.environ.get("STUNTING_MODEL_PATH", "models/stunting_model.pkl")
    UNDERWEIGHT_MODEL_PATH = os.environ.get("UNDERWEIGHT_MODEL_PATH", "models/underweight_model.pkl")

    # Free-text version labels surfaced in the UI and stored with every
    # prediction, one per target since each is an independently trained
    # artifact (Random Forest for stunting, XGBoost for underweight).
    STUNTING_MODEL_VERSION = os.environ.get("STUNTING_MODEL_VERSION", "car-mics6-stunting-rf-v1")
    UNDERWEIGHT_MODEL_VERSION = os.environ.get("UNDERWEIGHT_MODEL_VERSION", "car-mics6-underweight-xgb-v1")

    # Decision thresholds applied to predict_proba() to derive the
    # "at_risk" / "not_at_risk" label. These are NOT embedded in the
    # pickled pipelines - they were chosen during training by maximizing
    # F1 on held-out data (see docs/MODEL_INTEGRATION.md) and must be
    # applied by the application, not assumed to be 0.5.
    STUNTING_DECISION_THRESHOLD = float(os.environ.get("STUNTING_DECISION_THRESHOLD", "0.5"))
    UNDERWEIGHT_DECISION_THRESHOLD = float(os.environ.get("UNDERWEIGHT_DECISION_THRESHOLD", "0.275"))

    MOCK_MODEL_VERSION = os.environ.get("MOCK_MODEL_VERSION", "dev-mock-1.0")


config = Config()
