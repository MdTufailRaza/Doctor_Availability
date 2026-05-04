"""Appointment API routes."""

from flask import Blueprint, jsonify, request

from app.services.appointment_service import book_appointment, get_appointment, update_appointment_status
from app.utils.auth import require_roles


appointment_bp = Blueprint("appointment_bp", __name__, url_prefix="/api")


@appointment_bp.post("/appointments")
@require_roles("user", "admin")
def create_appointment():
    appointment = book_appointment(request.get_json(silent=True) or {})
    return jsonify({"message": "Appointment booked successfully.", "data": appointment.to_dict()}), 201


@appointment_bp.get("/appointments/<int:appointment_id>")
@require_roles("admin")
def get_appointment_status(appointment_id):
    appointment = get_appointment(appointment_id)
    return jsonify({"data": appointment.to_dict()})


@appointment_bp.patch("/appointments/<int:appointment_id>/status")
@require_roles("admin")
def patch_appointment_status(appointment_id):
    payload = request.get_json(silent=True) or {}
    appointment = update_appointment_status(appointment_id, payload.get("status"))
    return jsonify({"message": "Appointment status updated successfully.", "data": appointment.to_dict()})
