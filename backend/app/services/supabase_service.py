"""Singleton Supabase client for server-side (service-role) database access.

The backend is the only component that talks to Postgres directly. It
uses the service-role key, which bypasses Row Level Security, so every
route MUST perform its own authorization checks (see `app.utils.auth`)
before reading or writing data.
"""
from __future__ import annotations

from flask import current_app, g
from supabase import Client, create_client


def get_supabase() -> Client:
    if "supabase" not in g:
        url = current_app.config["SUPABASE_URL"]
        key = current_app.config["SUPABASE_SERVICE_ROLE_KEY"]
        if not url or not key:
            raise RuntimeError(
                "Supabase is not configured. Set SUPABASE_URL and "
                "SUPABASE_SERVICE_ROLE_KEY in the backend .env file."
            )
        g.supabase = create_client(url, key)
    return g.supabase
