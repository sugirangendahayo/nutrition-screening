"""Administrator-only user management.

New accounts are provisioned by an administrator (Supabase Auth has no
public self-registration in this system, matching the "Contact
Administrator" model in the research prototype). A temporary password is
generated and returned once in the API response for the administrator to
share with the new user out-of-band.
"""
import secrets

from flask import Blueprint, request

from app.utils.auth import ALL_ROLES, ROLE_ADMIN, require_role
from app.utils.responses import fail, ok
from app.services.supabase_service import get_supabase

bp = Blueprint("users", __name__, url_prefix="/api/users")


@bp.get("")
@require_role(ROLE_ADMIN)
def list_users():
    supabase = get_supabase()
    rows = (
        supabase.table("profiles")
        .select("id, full_name, role, facility, is_active, created_at")
        .order("created_at", desc=True)
        .execute()
        .data
        or []
    )
    return ok({"users": rows})


@bp.post("")
@require_role(ROLE_ADMIN)
def create_user():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip()
    full_name = (payload.get("fullName") or "").strip()
    role = payload.get("role")
    facility = payload.get("facility")

    if not email or not full_name:
        return fail("Email and full name are required.", status=422)
    if role not in ALL_ROLES:
        return fail("A valid role must be selected.", status=422)

    supabase = get_supabase()
    temp_password = secrets.token_urlsafe(12)

    try:
        created = supabase.auth.admin.create_user(
            {
                "email": email,
                "password": temp_password,
                "email_confirm": True,
            }
        )
    except Exception as exc:  # noqa: BLE001
        return fail(f"Could not create the account: {exc}", status=400)

    user_id = created.user.id

    # A database trigger already inserts a default profile row when the
    # auth user is created; upsert so our explicit values (role, name,
    # facility) always win.
    supabase.table("profiles").upsert(
        {
            "id": user_id,
            "full_name": full_name,
            "role": role,
            "facility": facility,
        }
    ).execute()

    return ok(
        {
            "id": user_id,
            "email": email,
            "fullName": full_name,
            "role": role,
            "temporaryPassword": temp_password,
        },
        status=201,
    )


@bp.patch("/<user_id>")
@require_role(ROLE_ADMIN)
def update_user(user_id: str):
    payload = request.get_json(silent=True) or {}
    updates = {}

    if "role" in payload:
        if payload["role"] not in ALL_ROLES:
            return fail("A valid role must be selected.", status=422)
        updates["role"] = payload["role"]
    if "isActive" in payload:
        updates["is_active"] = bool(payload["isActive"])
    if "fullName" in payload:
        updates["full_name"] = payload["fullName"]
    if "facility" in payload:
        updates["facility"] = payload["facility"]

    if not updates:
        return fail("No valid fields to update.", status=422)

    supabase = get_supabase()
    result = (
        supabase.table("profiles").update(updates).eq("id", user_id).execute()
    )
    if not result.data:
        return fail("User not found.", status=404)

    return ok(result.data[0])
