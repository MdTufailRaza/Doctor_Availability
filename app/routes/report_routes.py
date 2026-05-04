"""Reporting and health API routes."""

from flask import Blueprint, jsonify, request

from app.services.utilization_service import calculate_utilization
from app.utils.auth import require_roles
from app.utils.errors import APIError


report_bp = Blueprint("report_bp", __name__, url_prefix="/api")


@report_bp.get("/health")
def health_check():
    return jsonify({"message": "Doctor Availability Scheduler API is healthy."})


@report_bp.get("/utilization")
@require_roles("admin")
def get_utilization():
    required = ["doctor_id", "clinic_id", "start_date", "end_date"]
    missing = [key for key in required if not request.args.get(key)]
    if missing:
        raise APIError(f"Missing required query parameter(s): {', '.join(missing)}.", status_code=400)

    data = calculate_utilization(
        {
            "doctor_id": int(request.args["doctor_id"]),
            "clinic_id": int(request.args["clinic_id"]),
            "start_date": request.args["start_date"],
            "end_date": request.args["end_date"],
        }
    )
    return jsonify({"data": data})
