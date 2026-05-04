"""Doctor availability roster services."""

from app.extensions import db
from app.models import DoctorRoster
from app.services.clinic_service import assign_doctor_to_clinic, get_clinic
from app.services.doctor_service import find_doctor_by_id
from app.utils.date_utils import parse_time, ranges_overlap
from app.utils.errors import APIError
from app.utils.validators import ensure_required_fields, normalize_day


def add_roster(payload):
    """Add a recurring roster window for a doctor at a clinic."""

    ensure_required_fields(payload, ["doctor_id", "clinic_id", "day", "start_time", "end_time"])

    doctor = find_doctor_by_id(payload["doctor_id"])
    clinic = get_clinic(payload["clinic_id"])
    day = normalize_day(payload["day"])
    start_time = parse_time(payload["start_time"])
    end_time = parse_time(payload["end_time"])

    if start_time >= end_time:
        raise APIError("Roster start_time must be before end_time.", status_code=400)

    assign_doctor_to_clinic(doctor.id, clinic.id)

    existing_rosters = db.session.scalars(
        db.select(DoctorRoster).where(
            DoctorRoster.doctor_id == doctor.id,
            DoctorRoster.clinic_id == clinic.id,
            DoctorRoster.day == day,
        )
    ).all()

    for roster in existing_rosters:
        if ranges_overlap(start_time, end_time, roster.start_time, roster.end_time):
            raise APIError("Roster overlaps an existing availability window.", status_code=409)

    roster = DoctorRoster(
        doctor_id=doctor.id,
        clinic_id=clinic.id,
        day=day,
        start_time=start_time,
        end_time=end_time,
    )
    db.session.add(roster)
    db.session.commit()
    return roster


def list_rosters():
    """List all rosters."""

    query = db.select(DoctorRoster).order_by(DoctorRoster.day.asc(), DoctorRoster.start_time.asc())
    return db.session.scalars(query).all()
