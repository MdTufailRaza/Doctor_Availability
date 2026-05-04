"""Doctor and speciality API routes."""

from flask import Blueprint, jsonify, request

from app.services.doctor_service import create_doctor, list_doctors_by_speciality, list_specialities


doctor_bp = Blueprint("doctor_bp", __name__, url_prefix="/api")


@doctor_bp.post("/doctors")
def add_doctor():
    doctor = create_doctor(request.get_json(silent=True) or {})
    return jsonify({"message": "Doctor created successfully.", "data": doctor.to_dict()}), 201


@doctor_bp.get("/doctors")
def get_doctors():
    speciality = request.args.get("speciality")
    doctors = list_doctors_by_speciality(speciality)
    return jsonify({"data": [doctor.to_dict() for doctor in doctors]})


@doctor_bp.get("/specialities")
def get_specialities():
    specialities = list_specialities()
    return jsonify({"data": [speciality.to_dict() for speciality in specialities]})
