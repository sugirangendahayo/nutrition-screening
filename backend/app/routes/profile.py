from flask import Blueprint, g

from app.utils.auth import require_auth
from app.utils.responses import ok

bp = Blueprint("profile", __name__, url_prefix="/api/profile")


@bp.get("")
@require_auth
def get_profile():
    return ok(g.current_user)
