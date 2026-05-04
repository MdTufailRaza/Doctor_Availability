"""Admin-only API routes."""

from flask import Blueprint, jsonify, request

from app.services.admin_service import get_dashboard_statistics
from app.services.appointment_service import confirm_appointment, list_appointments, update_appointment_status
from app.services.patient_service import list_patients
from app.utils.auth import require_roles


admin_bp = Blueprint("admin_bp", __name__, url_prefix="/api/admin")


@admin_bp.get("/patients")
@require_roles("admin")
def get_patients():
    return jsonify({"data": list_patients()})


@admin_bp.get("/appointments")
@require_roles("admin")
def get_admin_appointments():
    appointments = list_appointments(request.args.get("status"))
    return jsonify({"data": [appointment.to_dict() for appointment in appointments]})


@admin_bp.post("/appointments/<int:appointment_id>/confirm")
@require_roles("admin")
def post_confirm_appointment(appointment_id):
    appointment = confirm_appointment(appointment_id)
    return jsonify({"message": "Appointment confirmed successfully.", "data": appointment.to_dict()})


@admin_bp.patch("/appointments/<int:appointment_id>/status")
@require_roles("admin")
def patch_admin_appointment_status(appointment_id):
    payload = request.get_json(silent=True) or {}
    appointment = update_appointment_status(appointment_id, payload.get("status"))
    return jsonify({"message": "Appointment status updated successfully.", "data": appointment.to_dict()})


@admin_bp.get("/stats")
@require_roles("admin")
def get_admin_stats():
    return jsonify({"data": get_dashboard_statistics()})
