"""Doctor-related business operations."""

from sqlalchemy import func

from app.extensions import db
from app.models import Doctor, Speciality
from app.utils.errors import APIError
from app.utils.validators import ensure_required_fields, normalize_speciality, normalize_text, validate_email


def _get_or_create_speciality(name):
    speciality_name = normalize_speciality(name)
    speciality = db.session.get(Speciality, speciality_name)
    if not speciality:
        speciality = Speciality(name=speciality_name, description=f"{speciality_name} speciality")
        db.session.add(speciality)
    return speciality_name


def create_doctor(payload):
    """Create a doctor with duplicate prevention."""

    ensure_required_fields(payload, ["name", "speciality", "email", "phone"])

    email = normalize_text(payload["email"]).lower()
    phone = normalize_text(payload["phone"])
    validate_email(email)

    if db.session.scalar(db.select(Doctor).where(func.lower(Doctor.email) == email)):
        raise APIError("Doctor with this email already exists.", status_code=409)
    if db.session.scalar(db.select(Doctor).where(Doctor.phone == phone)):
        raise APIError("Doctor with this phone already exists.", status_code=409)

    doctor = Doctor(
        name=normalize_text(payload["name"]),
        speciality=_get_or_create_speciality(payload["speciality"]),
        email=email,
        phone=phone,
        is_admin=bool(payload.get("is_admin", False)),
    )
    db.session.add(doctor)
    db.session.commit()
    return doctor


def list_doctors_by_speciality(speciality=None):
    """List doctors optionally filtered by speciality."""

    query = db.select(Doctor).order_by(Doctor.name.asc())
    if speciality:
        query = query.where(Doctor.speciality == normalize_speciality(speciality))
    return db.session.scalars(query).all()


def find_doctor_by_id(doctor_id):
    """Return a doctor or raise 404."""

    doctor = db.session.get(Doctor, doctor_id)
    if not doctor:
        raise APIError("Doctor not found.", status_code=404)
    return doctor


def list_specialities():
    """Return the speciality catalogue."""

    query = db.select(Speciality).order_by(Speciality.name.asc())
    return db.session.scalars(query).all()
