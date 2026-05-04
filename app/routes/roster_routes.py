"""Roster API routes."""

from flask import Blueprint, jsonify, request

from app.services.roster_service import add_roster, list_rosters


roster_bp = Blueprint("roster_bp", __name__, url_prefix="/api")


@roster_bp.post("/rosters")
def create_roster():
    roster = add_roster(request.get_json(silent=True) or {})
    return jsonify({"message": "Roster created successfully.", "data": roster.to_dict()}), 201


@roster_bp.get("/rosters")
def get_rosters():
    rosters = list_rosters()
    return jsonify({"data": [roster.to_dict() for roster in rosters]})
