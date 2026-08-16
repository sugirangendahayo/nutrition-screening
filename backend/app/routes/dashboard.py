from flask import Blueprint

from app.services.dashboard_service import get_dashboard_summary
from app.services.supabase_service import get_supabase
from app.utils.auth import require_auth
from app.utils.responses import ok

bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@bp.get("")
@require_auth
def dashboard():
    supabase = get_supabase()
    summary = get_dashboard_summary(supabase)
    return ok(summary)
