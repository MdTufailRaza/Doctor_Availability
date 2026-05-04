"""Patient API routes."""

from flask import Blueprint, jsonify, request

from app.services.patient_service import create_patient
from app.utils.auth import require_roles


patient_bp = Blueprint("patient_bp", __name__, url_prefix="/api")


@patient_bp.post("/patients")
@require_roles("user", "admin")
def add_patient():
    patient = create_patient(request.get_json(silent=True) or {})
    return jsonify({"message": "Patient created successfully.", "data": patient.to_dict()}), 201
