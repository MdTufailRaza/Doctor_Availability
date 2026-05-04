"""Clinic and doctor-clinic mapping services."""

from sqlalchemy import and_, func

from app.extensions import db
from app.models import Clinic, Doctor, DoctorClinicMapping
from app.services.doctor_service import create_doctor, find_doctor_by_id
from app.utils.errors import APIError
from app.utils.validators import ensure_required_fields, normalize_text


def _ensure_admin_gynecology_doctor():
    doctor = db.session.scalar(
        db.select(Doctor).where(
            and_(Doctor.is_admin.is_(True), func.lower(Doctor.speciality) == "gynecology")
        )
    )
    if doctor:
        return doctor

    return create_doctor(
        {
            "name": "Platform Gynecology Admin",
            "speciality": "Gynecology",
            "email": "admin.gynecology@platform.local",
            "phone": "9000000000",
            "is_admin": True,
        }
    )


def assign_doctor_to_clinic(doctor_id, clinic_id):
    """Create a doctor-clinic mapping if it does not already exist."""

    doctor = find_doctor_by_id(doctor_id)
    clinic = get_clinic(clinic_id)

    mapping = db.session.get(DoctorClinicMapping, {"doctor_id": doctor.id, "clinic_id": clinic.id})
    if mapping:
        return mapping

    mapping = DoctorClinicMapping(doctor_id=doctor.id, clinic_id=clinic.id)
    db.session.add(mapping)
    db.session.commit()
    return mapping


def create_clinic(payload):
    """Create a clinic and auto-assign the admin gynecology doctor."""

    ensure_required_fields(payload, ["name", "location"])

    name = normalize_text(payload["name"])
    location = normalize_text(payload["location"])

    existing = db.session.scalar(
        db.select(Clinic).where(and_(func.lower(Clinic.name) == name.lower(), func.lower(Clinic.location) == location.lower()))
    )
    if existing:
        raise APIError("Clinic with this name and location already exists.", status_code=409)

    clinic = Clinic(name=name, location=location)
    db.session.add(clinic)
    db.session.commit()

    admin_doctor = _ensure_admin_gynecology_doctor()
    mapping = assign_doctor_to_clinic(admin_doctor.id, clinic.id)

    return clinic, mapping.doctor


def get_clinic(clinic_id):
    """Return a clinic or raise 404."""

    clinic = db.session.get(Clinic, clinic_id)
    if not clinic:
        raise APIError("Clinic not found.", status_code=404)
    return clinic


def list_clinics():
    """List all clinics with their doctors."""

    query = db.select(Clinic).order_by(Clinic.name.asc())
    return db.session.scalars(query).all()
