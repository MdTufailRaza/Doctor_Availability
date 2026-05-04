"""Appointment lifecycle services."""

from datetime import datetime

from app.extensions import db
from app.models import Appointment, AppointmentStatus, DoctorRoster
from app.services.clinic_service import get_clinic
from app.services.doctor_service import find_doctor_by_id
from app.services.leave_service import doctor_is_on_leave
from app.services.patient_service import find_patient_by_id
from app.utils.constants import FINAL_APPOINTMENT_STATUSES
from app.utils.date_utils import (
    day_name_for_date,
    enforce_15_minute_slot,
    enforce_future_datetime,
    parse_date,
    parse_time,
)
from app.utils.errors import APIError
from app.utils.validators import ensure_required_fields


def _doctor_has_roster(doctor_id, clinic_id, appointment_date, appointment_time):
    roster = db.session.scalar(
        db.select(DoctorRoster).where(
            DoctorRoster.doctor_id == doctor_id,
            DoctorRoster.clinic_id == clinic_id,
            DoctorRoster.day == day_name_for_date(appointment_date),
            DoctorRoster.start_time <= appointment_time,
            DoctorRoster.end_time > appointment_time,
        )
    )
    return roster


def book_appointment(payload):
    """Book an appointment with full scheduling validation."""

    ensure_required_fields(payload, ["patient_id", "doctor_id", "clinic_id", "date", "time"])

    patient = find_patient_by_id(payload["patient_id"])
    doctor = find_doctor_by_id(payload["doctor_id"])
    clinic = get_clinic(payload["clinic_id"])
    appointment_date = parse_date(payload["date"])
    appointment_time = parse_time(payload["time"])

    enforce_future_datetime(appointment_date, appointment_time)
    enforce_15_minute_slot(appointment_time)

    roster = _doctor_has_roster(doctor.id, clinic.id, appointment_date, appointment_time)
    if not roster:
        raise APIError("Appointment is outside the doctor's working hours.", status_code=400)

    if doctor_is_on_leave(doctor.id, appointment_date):
        raise APIError("Doctor is on leave for the selected date.", status_code=409)

    existing_for_doctor = db.session.scalar(
        db.select(Appointment).where(
            Appointment.doctor_id == doctor.id,
            Appointment.clinic_id == clinic.id,
            Appointment.date == appointment_date,
            Appointment.time == appointment_time,
            Appointment.status != AppointmentStatus.CANCELLED,
        )
    )
    if existing_for_doctor:
        raise APIError("Doctor already has an appointment for this slot.", status_code=409)

    existing_for_patient = db.session.scalar(
        db.select(Appointment).where(
            Appointment.patient_id == patient.id,
            Appointment.date == appointment_date,
            Appointment.time == appointment_time,
            Appointment.status != AppointmentStatus.CANCELLED,
        )
    )
    if existing_for_patient:
        raise APIError("Patient already has an appointment for this slot.", status_code=409)

    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        clinic_id=clinic.id,
        date=appointment_date,
        time=appointment_time,
        is_confirmed=False,
        status=AppointmentStatus.BOOKED,
    )
    db.session.add(appointment)
    db.session.commit()
    return appointment


def update_appointment_status(appointment_id, status_value):
    """Update appointment status based on allowed lifecycle transitions."""

    appointment = get_appointment(appointment_id)
    normalized_status = str(status_value or "").strip().upper()

    try:
        new_status = AppointmentStatus(normalized_status)
    except ValueError as exc:
        allowed = ", ".join(status.value for status in AppointmentStatus)
        raise APIError(f"Invalid appointment status. Allowed values: {allowed}.", status_code=400) from exc

    current_status = appointment.status.value
    if current_status in FINAL_APPOINTMENT_STATUSES:
        raise APIError("Finalized appointments cannot be updated again.", status_code=409)
    if new_status.value == AppointmentStatus.BOOKED.value:
        raise APIError("Appointments cannot transition back to BOOKED.", status_code=400)
    if not appointment.is_confirmed and new_status in {AppointmentStatus.COMPLETED, AppointmentStatus.NOSHOW}:
        raise APIError("Appointment must be confirmed before completion or no-show updates.", status_code=409)

    appointment.status = new_status
    db.session.commit()
    return appointment


def get_appointment(appointment_id):
    """Return an appointment or raise 404."""

    appointment = db.session.get(Appointment, appointment_id)
    if not appointment:
        raise APIError("Appointment not found.", status_code=404)
    return appointment


def list_appointments(status=None):
    """Return appointments for admin review."""

    query = db.select(Appointment).order_by(Appointment.date.asc(), Appointment.time.asc())
    if status:
        try:
            normalized_status = AppointmentStatus(str(status).strip().upper())
        except ValueError as exc:
            allowed = ", ".join(value.value for value in AppointmentStatus)
            raise APIError(f"Invalid appointment status. Allowed values: {allowed}.", status_code=400) from exc
        query = query.where(Appointment.status == normalized_status)
    return db.session.scalars(query).all()


def confirm_appointment(appointment_id):
    """Mark a booked appointment as confirmed by the admin."""

    appointment = get_appointment(appointment_id)
    if appointment.status != AppointmentStatus.BOOKED:
        raise APIError("Only booked appointments can be confirmed.", status_code=409)
    if appointment.is_confirmed:
        raise APIError("Appointment is already confirmed.", status_code=409)

    appointment.is_confirmed = True
    appointment.confirmed_at = datetime.utcnow()
    db.session.commit()
    return appointment
