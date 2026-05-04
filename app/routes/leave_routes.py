"""Doctor leave API routes."""

from flask import Blueprint, jsonify, request

from app.services.leave_service import add_leave


leave_bp = Blueprint("leave_bp", __name__, url_prefix="/api")


@leave_bp.post("/leaves")
def create_leave():
    leave = add_leave(request.get_json(silent=True) or {})
    return jsonify({"message": "Doctor leave added successfully.", "data": leave.to_dict()}), 201
