"""Clinic and doctor-clinic mapping API routes."""

from flask import Blueprint, jsonify, request

from app.services.clinic_service import assign_doctor_to_clinic, create_clinic, get_clinic, list_clinics


clinic_bp = Blueprint("clinic_bp", __name__, url_prefix="/api")


@clinic_bp.post("/clinics")
def add_clinic():
    clinic, admin_doctor = create_clinic(request.get_json(silent=True) or {})
    return (
        jsonify(
            {
                "message": "Clinic created successfully.",
                "data": clinic.to_dict(include_doctors=True),
                "auto_assigned_gynecology_doctor": admin_doctor.to_dict(),
            }
        ),
        201,
    )


@clinic_bp.get("/clinics")
def get_clinics():
    clinics = list_clinics()
    return jsonify({"data": [clinic.to_dict(include_doctors=True) for clinic in clinics]})


@clinic_bp.get("/clinics/<int:clinic_id>")
def clinic_detail(clinic_id):
    clinic = get_clinic(clinic_id)
    return jsonify({"data": clinic.to_dict(include_doctors=True)})


@clinic_bp.post("/mappings")
def map_doctor_to_clinic():
    payload = request.get_json(silent=True) or {}
    mapping = assign_doctor_to_clinic(payload.get("doctor_id"), payload.get("clinic_id"))
    return jsonify({"message": "Doctor mapped to clinic successfully.", "data": mapping.to_dict()}), 201
