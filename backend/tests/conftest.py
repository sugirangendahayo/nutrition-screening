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


VALID_SCREENING_INPUT = {
    "child_age_months": 24,
    "sex": "male",
    "weight_kg": 10.5,
    "height_cm": 82.0,
    "breastfeeding_status": "no_longer_breastfeeding",
    "mother_education_level": "secondary",
    "household_wealth_index": "middle",
    "residence_type": "urban",
    "drinking_water_source": "improved",
    "sanitation_facility": "improved",
    "vitamin_a_supplementation": "yes",
    "immunization_status": "fully_immunized",
}
