"""Consistent JSON response envelope used across the entire API."""
from flask import jsonify


def ok(data=None, status: int = 200):
    return jsonify({"success": True, "data": data, "error": None}), status


def fail(message: str, status: int = 400, details=None):
    error = {"message": message}
    if details is not None:
        error["details"] = details
    return jsonify({"success": False, "data": None, "error": error}), status
