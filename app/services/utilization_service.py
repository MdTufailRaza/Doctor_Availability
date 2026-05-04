"""Utilization reporting services."""

from datetime import timedelta

from app.extensions import db
from app.models import Appointment, AppointmentStatus, DoctorRoster
from app.services.leave_service import doctor_is_on_leave
from app.utils.date_utils import day_name_for_date, generate_slots, parse_date


def calculate_utilization(filters):
    """Calculate booked slot utilization across a date range."""

    start_date = parse_date(filters["start_date"])
    end_date = parse_date(filters["end_date"])
    doctor_id = filters["doctor_id"]
    clinic_id = filters["clinic_id"]

    total_slots = 0
    current_date = start_date
    while current_date <= end_date:
        if not doctor_is_on_leave(doctor_id, current_date):
            rosters = db.session.scalars(
                db.select(DoctorRoster).where(
                    DoctorRoster.doctor_id == doctor_id,
                    DoctorRoster.clinic_id == clinic_id,
                    DoctorRoster.day == day_name_for_date(current_date),
                )
            ).all()
            for roster in rosters:
                total_slots += len(generate_slots(roster.start_time, roster.end_time))
        current_date += timedelta(days=1)

    booked_slots = db.session.scalar(
        db.select(db.func.count(Appointment.id)).where(
            Appointment.doctor_id == doctor_id,
            Appointment.clinic_id == clinic_id,
            Appointment.date >= start_date,
            Appointment.date <= end_date,
            Appointment.status.in_(
                [AppointmentStatus.BOOKED, AppointmentStatus.COMPLETED, AppointmentStatus.NOSHOW]
            ),
        )
    ) or 0

    utilization = round(booked_slots / total_slots, 4) if total_slots else 0.0

    return {
        "doctor_id": doctor_id,
        "clinic_id": clinic_id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "booked_slots": booked_slots,
        "total_slots": total_slots,
        "utilization": utilization,
    }
