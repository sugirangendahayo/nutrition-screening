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
    # trained artifact is available yet. "production" requires a real model.
    ML_MODEL_STATUS = os.environ.get("ML_MODEL_STATUS", "development")

    # "single_multioutput" or "dual_model"
    MODEL_MODE = os.environ.get("MODEL_MODE", "dual_model")

    MODEL_PATH = os.environ.get("MODEL_PATH", "models/model.joblib")
    STUNTING_MODEL_PATH = os.environ.get("STUNTING_MODEL_PATH", "models/stunting_model.joblib")
    UNDERWEIGHT_MODEL_PATH = os.environ.get("UNDERWEIGHT_MODEL_PATH", "models/underweight_model.joblib")
    PREPROCESSOR_PATH = os.environ.get("PREPROCESSOR_PATH", "")

    # Small representative sample of training-like rows (joblib-pickled
    # pandas DataFrame) used as the SHAP background distribution for local
    # explanations. Optional - falls back to global importance if absent.
    BACKGROUND_DATA_PATH = os.environ.get("BACKGROUND_DATA_PATH", "")

    MODEL_VERSION = os.environ.get("MODEL_VERSION", "dev-mock-1.0")

    @property
    def is_production_model(self) -> bool:
        return self.ML_MODEL_STATUS == "production"


config = Config()
