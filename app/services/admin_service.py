"""Admin reporting services."""

from app.extensions import db
from app.models import Appointment, AppointmentStatus, Clinic, Doctor, Patient
from app.utils.date_utils import now_local


def get_dashboard_statistics():
    """Build aggregate statistics for the admin dashboard."""

    total_patients = db.session.scalar(db.select(db.func.count(Patient.id))) or 0
    total_doctors = db.session.scalar(db.select(db.func.count(Doctor.id))) or 0
    total_clinics = db.session.scalar(db.select(db.func.count(Clinic.id))) or 0
    total_appointments = db.session.scalar(db.select(db.func.count(Appointment.id))) or 0
    pending_confirmation = db.session.scalar(
        db.select(db.func.count(Appointment.id)).where(
            Appointment.status == AppointmentStatus.BOOKED,
            Appointment.is_confirmed.is_(False),
        )
    ) or 0
    confirmed_booked = db.session.scalar(
        db.select(db.func.count(Appointment.id)).where(
            Appointment.status == AppointmentStatus.BOOKED,
            Appointment.is_confirmed.is_(True),
        )
    ) or 0
    today = now_local().date()
    todays_appointments = db.session.scalar(
        db.select(db.func.count(Appointment.id)).where(Appointment.date == today)
    ) or 0

    by_status = {}
    for status in AppointmentStatus:
        by_status[status.value] = db.session.scalar(
            db.select(db.func.count(Appointment.id)).where(Appointment.status == status)
        ) or 0

    return {
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "total_clinics": total_clinics,
        "total_appointments": total_appointments,
        "pending_confirmation": pending_confirmation,
        "confirmed_booked": confirmed_booked,
        "todays_appointments": todays_appointments,
        "appointments_by_status": by_status,
    }
