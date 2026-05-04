"""Search and calculate availability windows."""

from sqlalchemy import and_, or_

from app.extensions import db
from app.models import Appointment, AppointmentStatus, Doctor, DoctorRoster
from app.services.leave_service import doctor_is_on_leave
from app.utils.date_utils import day_name_for_date, generate_slots, parse_date, parse_time, serialize_date, serialize_time


def search_availability(filters):
    """Search doctor availability by doctor name, speciality, date, or time range."""

    date_filter = parse_date(filters["date"]) if filters.get("date") else None
    start_time_filter = parse_time(filters["start_time"]) if filters.get("start_time") else None
    end_time_filter = parse_time(filters["end_time"]) if filters.get("end_time") else None

    query = db.select(DoctorRoster).join(Doctor).order_by(Doctor.name.asc(), DoctorRoster.day.asc(), DoctorRoster.start_time.asc())

    doctor_name = filters.get("doctor_name")
    if doctor_name:
        query = query.where(Doctor.name.ilike(f"%{doctor_name.strip()}%"))

    speciality = filters.get("speciality")
    if speciality:
        query = query.where(Doctor.speciality == speciality.strip().title())

    clinic_id = filters.get("clinic_id")
    if clinic_id:
        query = query.where(DoctorRoster.clinic_id == clinic_id)

    rosters = db.session.scalars(query).all()

    if date_filter:
        roster_day = day_name_for_date(date_filter)
        rosters = [roster for roster in rosters if roster.day == roster_day]

    response = []
    for roster in rosters:
        if date_filter:
            if doctor_is_on_leave(roster.doctor_id, date_filter):
                continue

            booked_appointments = db.session.scalars(
                db.select(Appointment).where(
                    Appointment.doctor_id == roster.doctor_id,
                    Appointment.clinic_id == roster.clinic_id,
                    Appointment.date == date_filter,
                    Appointment.status != AppointmentStatus.CANCELLED,
                )
            ).all()
            booked_times = {appointment.time for appointment in booked_appointments}

            slots = [
                slot
                for slot in generate_slots(roster.start_time, roster.end_time)
                if slot not in booked_times
                and (start_time_filter is None or slot >= start_time_filter)
                and (end_time_filter is None or slot < end_time_filter)
            ]
            if not slots:
                continue

            response.append(
                {
                    "doctor_id": roster.doctor_id,
                    "doctor_name": roster.doctor.name,
                    "speciality": roster.doctor.speciality,
                    "clinic": roster.clinic.name,
                    "clinic_id": roster.clinic_id,
                    "date": serialize_date(date_filter),
                    "day": roster.day,
                    "available_time": [serialize_time(slot) for slot in slots],
                }
            )
            continue

        if start_time_filter and roster.end_time <= start_time_filter:
            continue
        if end_time_filter and roster.start_time >= end_time_filter:
            continue

        response.append(
            {
                "doctor_id": roster.doctor_id,
                "doctor_name": roster.doctor.name,
                "speciality": roster.doctor.speciality,
                "clinic": roster.clinic.name,
                "clinic_id": roster.clinic_id,
                "day": roster.day,
                "available_time": f"{serialize_time(roster.start_time)} - {serialize_time(roster.end_time)}",
            }
        )

    return response
