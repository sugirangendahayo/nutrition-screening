"""Authentication and authorization helpers.

Supabase Auth issues the JWT access token to the frontend after login.
The frontend forwards it as `Authorization: Bearer <token>` on every
request to this API. We verify the token's signature locally, then look
up the user's role from the `profiles` table (never trusting a role
claim supplied by the client).

Supabase projects sign access tokens one of two ways (see
https://supabase.com/docs/guides/auth/signing-keys):

- Legacy projects: a single shared secret, HS256 (`SUPABASE_JWT_SECRET`).
- Newer projects (default since mid-2025): asymmetric keys (ES256/RS256),
  verified with the project's public JWKS
  (`<SUPABASE_URL>/auth/v1/.well-known/jwks.json`) - no shared secret
  involved at all.

We inspect the token's own `alg` header (unverified - it only selects
*how* to verify, the signature check itself still fails for a tampered
token) and dispatch to whichever method applies, so this backend works
against either kind of project without extra configuration.
"""
from __future__ import annotations

from functools import wraps

import jwt
from flask import current_app, g, request

from app.services.supabase_service import get_supabase
from app.utils.responses import fail

_jwks_clients: dict[str, "jwt.PyJWKClient"] = {}


def _get_jwks_client(supabase_url: str) -> "jwt.PyJWKClient":
    """Cached PyJWKClient for the project's public signing keys.

    PyJWKClient caches the fetched key set in-process and only re-fetches
    when it encounters an unknown `kid`, so this does not hit the network
    on every request.
    """
    if supabase_url not in _jwks_clients:
        jwks_url = supabase_url.rstrip("/") + "/auth/v1/.well-known/jwks.json"
        _jwks_clients[supabase_url] = jwt.PyJWKClient(jwks_url, cache_keys=True)
    return _jwks_clients[supabase_url]

ROLE_ADMIN = "administrator"
ROLE_HEALTHCARE_WORKER = "healthcare_worker"
ROLE_NUTRITION_OFFICER = "nutrition_officer"
ROLE_RESEARCHER = "researcher"

ALL_ROLES = (ROLE_ADMIN, ROLE_HEALTHCARE_WORKER, ROLE_NUTRITION_OFFICER, ROLE_RESEARCHER)


class AuthError(Exception):
    def __init__(self, message: str, status: int = 401):
        self.message = message
        self.status = status
        super().__init__(message)


def _extract_token() -> str:
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        raise AuthError("Missing or malformed Authorization header.")
    return header.split(" ", 1)[1].strip()


def _decode_token(token: str) -> dict:
    try:
        header = jwt.get_unverified_header(token)
    except jwt.PyJWTError as exc:
        raise AuthError(f"Invalid or expired session: {exc}") from exc

    algorithm = header.get("alg", "HS256")

    try:
        if algorithm == "HS256":
            secret = current_app.config.get("SUPABASE_JWT_SECRET")
            if not secret:
                raise AuthError("Server is not configured for authentication.", status=500)
            return jwt.decode(token, secret, algorithms=["HS256"], audience="authenticated")

        # Asymmetric signing keys (ES256/RS256) - verify against the
        # project's public JWKS instead of a shared secret.
        supabase_url = current_app.config.get("SUPABASE_URL")
        if not supabase_url:
            raise AuthError("Server is not configured for authentication.", status=500)
        signing_key = _get_jwks_client(supabase_url).get_signing_key_from_jwt(token)
        return jwt.decode(token, signing_key.key, algorithms=[algorithm], audience="authenticated")
    except jwt.PyJWTError as exc:
        raise AuthError(f"Invalid or expired session: {exc}") from exc


def load_current_user() -> dict:
    """Verify the bearer token and fetch the caller's profile (id + role)."""
    token = _extract_token()
    claims = _decode_token(token)
    user_id = claims.get("sub")
    if not user_id:
        raise AuthError("Token missing subject claim.")

    supabase = get_supabase()
    result = (
        supabase.table("profiles")
        .select("id, full_name, role, facility, is_active")
        .eq("id", user_id)
        .single()
        .execute()
    )
    profile = result.data
    if not profile:
        raise AuthError("No profile found for this account. Contact an administrator.", status=403)
    if not profile.get("is_active", True):
        raise AuthError("This account has been deactivated.", status=403)

    return {
        "id": profile["id"],
        "email": claims.get("email"),
        "full_name": profile.get("full_name"),
        "role": profile.get("role"),
        "facility": profile.get("facility"),
    }


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            g.current_user = load_current_user()
        except AuthError as exc:
            return fail(exc.message, status=exc.status)
        return fn(*args, **kwargs)

    return wrapper


def require_role(*allowed_roles: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                g.current_user = load_current_user()
            except AuthError as exc:
                return fail(exc.message, status=exc.status)

            if g.current_user["role"] not in allowed_roles:
                return fail(
                    "You do not have permission to perform this action.", status=403
                )
            return fn(*args, **kwargs)

        return wrapper

    return decorator
