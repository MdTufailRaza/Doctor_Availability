"""Doctor leave services."""

from app.extensions import db
from app.models import DoctorLeave
from app.services.doctor_service import find_doctor_by_id
from app.utils.constants import ALLOWED_LEAVE_REASONS
from app.utils.date_utils import parse_date
from app.utils.errors import APIError
from app.utils.validators import ensure_required_fields, normalize_text


def add_leave(payload):
    """Create a leave entry after taxonomy and date validation."""

    ensure_required_fields(payload, ["doctor_id", "start_date", "end_date", "reason"])

    doctor = find_doctor_by_id(payload["doctor_id"])
    start_date = parse_date(payload["start_date"])
    end_date = parse_date(payload["end_date"])
    reason = normalize_text(payload["reason"]).upper()

    if start_date > end_date:
        raise APIError("Leave start_date must be before or equal to end_date.", status_code=400)
    if reason not in ALLOWED_LEAVE_REASONS:
        raise APIError(
            f"Leave reason must be one of: {', '.join(sorted(ALLOWED_LEAVE_REASONS))}.",
            status_code=400,
        )

    overlapping_leave = db.session.scalar(
        db.select(DoctorLeave).where(
            DoctorLeave.doctor_id == doctor.id,
            DoctorLeave.start_date <= end_date,
            DoctorLeave.end_date >= start_date,
        )
    )
    if overlapping_leave:
        raise APIError("Doctor already has leave recorded in the selected date range.", status_code=409)

    leave = DoctorLeave(
        doctor_id=doctor.id,
        start_date=start_date,
        end_date=end_date,
        reason=reason,
    )
    db.session.add(leave)
    db.session.commit()
    return leave


def doctor_is_on_leave(doctor_id, target_date):
    """Return True when a doctor is on leave for a date."""

    leave = db.session.scalar(
        db.select(DoctorLeave).where(
            DoctorLeave.doctor_id == doctor_id,
            DoctorLeave.start_date <= target_date,
            DoctorLeave.end_date >= target_date,
        )
    )
    return leave is not None
