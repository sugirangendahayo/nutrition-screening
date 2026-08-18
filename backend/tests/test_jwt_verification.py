"""Regression tests for dual-mode Supabase JWT verification.

Supabase projects sign access tokens one of two ways (see
https://supabase.com/docs/guides/auth/signing-keys):

- Legacy projects: HS256 with a single shared secret (`SUPABASE_JWT_SECRET`).
- Newer projects (default since mid-2025): asymmetric ES256/RS256, verified
  against the project's public JWKS endpoint - no shared secret involved.

`app.utils.auth._decode_token` must transparently support both, since a
backend hard-coded to HS256-only verification silently rejects every
request (401) against any newly created Supabase project, even with a
100% correctly configured `SUPABASE_JWT_SECRET`.
"""
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec

from app.utils import auth as auth_module


def _payload():
    now = datetime.now(timezone.utc)
    return {
        "sub": "00000000-0000-0000-0000-000000000001",
        "email": "user@example.com",
        "role": "authenticated",
        "aud": "authenticated",
        "iat": now,
        "exp": now + timedelta(hours=1),
    }


def test_decode_token_accepts_legacy_hs256(app):
    with app.app_context():
        app.config["SUPABASE_JWT_SECRET"] = "test-secret"
        token = jwt.encode(_payload(), "test-secret", algorithm="HS256")

        claims = auth_module._decode_token(token)

        assert claims["sub"] == "00000000-0000-0000-0000-000000000001"


def test_decode_token_accepts_asymmetric_es256_via_jwks(app, mocker):
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    token = jwt.encode(_payload(), private_key, algorithm="ES256", headers={"kid": "test-kid"})

    fake_signing_key = mocker.Mock(key=public_key)
    fake_jwks_client = mocker.Mock()
    fake_jwks_client.get_signing_key_from_jwt.return_value = fake_signing_key
    mocker.patch.object(auth_module, "_get_jwks_client", return_value=fake_jwks_client)

    with app.app_context():
        app.config["SUPABASE_URL"] = "https://example.supabase.co"

        claims = auth_module._decode_token(token)

        assert claims["sub"] == "00000000-0000-0000-0000-000000000001"
        fake_jwks_client.get_signing_key_from_jwt.assert_called_once_with(token)


def test_decode_token_rejects_tampered_asymmetric_signature(app, mocker):
    private_key = ec.generate_private_key(ec.SECP256R1())
    other_key = ec.generate_private_key(ec.SECP256R1())  # wrong key, simulates forgery

    token = jwt.encode(_payload(), private_key, algorithm="ES256", headers={"kid": "test-kid"})

    fake_signing_key = mocker.Mock(key=other_key.public_key())
    fake_jwks_client = mocker.Mock()
    fake_jwks_client.get_signing_key_from_jwt.return_value = fake_signing_key
    mocker.patch.object(auth_module, "_get_jwks_client", return_value=fake_jwks_client)

    with app.app_context():
        app.config["SUPABASE_URL"] = "https://example.supabase.co"

        with pytest.raises(auth_module.AuthError):
            auth_module._decode_token(token)
