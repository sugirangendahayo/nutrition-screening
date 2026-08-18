import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

os.environ.setdefault("ML_MODEL_STATUS", "development")
os.environ.setdefault("SUPABASE_JWT_SECRET", "test-secret")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-key")

from app import create_app
from app.config import Config


@pytest.fixture
def app():
    cfg = Config()
    cfg.ML_MODEL_STATUS = "development"
    flask_app = create_app(cfg)
    flask_app.config.update(TESTING=True)
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_as(mocker):
    """Return a helper to stub the authenticated user for a given role."""

    def _auth_as(role: str, user_id: str = "00000000-0000-0000-0000-000000000001"):
        mocker.patch(
            "app.utils.auth.load_current_user",
            return_value={
                "id": user_id,
                "email": "test@example.com",
                "full_name": "Test User",
                "role": role,
                "facility": None,
            },
        )

    return _auth_as


# Matches the exact 20 raw MICS6 predictor codes expected by the trained
# pipelines (see app.ml.feature_schema.RAW_FEATURE_ORDER).
VALID_SCREENING_INPUT = {
    "CAGE": 24,
    "HL4": "1.0",
    "CA31": "1.0",
    "IM2": "1.0",
    "BD2": "1.0",
    "cdisability": "1.0",
    "cinsurance": "1.0",
    "melevel": "0.0",
    "caretakerdis": "1.0",
    "HH6": "1.0",
    "HH7": "1.0",
    "windex5": "1.0",
    "religion": "1.0",
    "ethnicity": "1.0",
    "CA1": "1.0",
    "CA14": "1.0",
    "CA16": "1.0",
    "CA17": "1.0",
    "TN3": "1.0",
    "EC1": "0.0",
}
