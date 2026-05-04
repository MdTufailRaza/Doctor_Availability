"""Date and time utilities for scheduling logic."""

from datetime import date, datetime, time, timedelta

from flask import current_app

from app.utils.errors import APIError


def now_local():
    """Return the current local datetime without external timezone data dependencies."""

    return datetime.now()


def parse_date(value):
    """Parse an ISO date string."""

    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError as exc:
        raise APIError("Date must use YYYY-MM-DD format.", status_code=400) from exc


def parse_time(value):
    """Parse an HH:MM time string."""

    if isinstance(value, time):
        return value.replace(second=0, microsecond=0)
    try:
        return datetime.strptime(str(value), "%H:%M").time()
    except ValueError as exc:
        raise APIError("Time must use HH:MM 24-hour format.", status_code=400) from exc


def serialize_date(value):
    """Serialize date values to ISO strings."""

    return value.isoformat() if value else None


def serialize_time(value):
    """Serialize time values to HH:MM strings."""

    return value.strftime("%H:%M") if value else None


def serialize_datetime(value):
    """Serialize datetime values to ISO strings."""

    return value.isoformat() if value else None


def day_name_for_date(value):
    """Convert a date into the domain weekday constant."""

    return value.strftime("%A").upper()


def slot_minutes():
    """Return the configured slot size in minutes."""

    return current_app.config["APPOINTMENT_SLOT_MINUTES"]


def enforce_future_datetime(appointment_date, appointment_time):
    """Ensure appointments are not booked in the past."""

    now = now_local()
    if appointment_date < now.date():
        raise APIError("Appointment date must be today or later.", status_code=400)
    if appointment_date == now.date() and appointment_time < now.time().replace(second=0, microsecond=0):
        raise APIError("Appointment time must be in the future.", status_code=400)


def enforce_15_minute_slot(appointment_time):
    """Ensure the appointment time sits on a 15-minute boundary."""

    if appointment_time.minute % slot_minutes() != 0:
        raise APIError("Appointment time must align to a 15-minute slot.", status_code=400)


def generate_slots(start_time, end_time):
    """Generate 15-minute slots from a start and end window."""

    current = datetime.combine(date.today(), start_time)
    boundary = datetime.combine(date.today(), end_time)
    step = timedelta(minutes=slot_minutes())
    slots = []

    while current < boundary:
        slots.append(current.time().replace(second=0, microsecond=0))
        current += step

    return slots


def ranges_overlap(start_a, end_a, start_b, end_b):
    """Return True when two time ranges overlap."""

    return start_a < end_b and start_b < end_a
