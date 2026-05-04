"""Authentication API routes."""

from flask import Blueprint, jsonify, request

from app.services.auth_service import authenticate
from app.utils.auth import get_current_user, login_user, logout_user


auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")


@auth_bp.post("/login")
def api_login():
    payload = request.get_json(silent=True) or {}
    user = authenticate(payload.get("role"), payload.get("username"), payload.get("password"))
    login_user(user["role"], user["username"], user["display_name"])
    return jsonify({"message": "Login successful.", "data": user})


@auth_bp.post("/logout")
def api_logout():
    logout_user()
    return jsonify({"message": "Logged out successfully."})


@auth_bp.get("/session")
def session_status():
    auth_user = get_current_user()
    return jsonify({"data": auth_user})
