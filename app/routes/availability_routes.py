"""Availability search API routes."""

from flask import Blueprint, jsonify, request

from app.services.availability_service import search_availability


availability_bp = Blueprint("availability_bp", __name__, url_prefix="/api")


@availability_bp.get("/availability")
def get_availability():
    availability = search_availability(request.args)
    return jsonify({"data": availability})
