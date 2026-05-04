"""Patient services."""

from sqlalchemy import func

from app.extensions import db
from app.models import Patient
from app.utils.errors import APIError
from app.utils.validators import ensure_required_fields, normalize_text


def create_patient(payload):
    """Create a patient after duplicate validation."""

    ensure_required_fields(payload, ["name", "contact"])
    name = normalize_text(payload["name"])
    contact = normalize_text(payload["contact"])

    existing = db.session.scalar(db.select(Patient).where(func.lower(Patient.contact) == contact.lower()))
    if existing:
        raise APIError("Patient with this contact already exists.", status_code=409)

    patient = Patient(name=name, contact=contact)
    db.session.add(patient)
    db.session.commit()
    return patient


def find_patient_by_id(patient_id):
    """Return a patient or raise 404."""

    patient = db.session.get(Patient, patient_id)
    if not patient:
        raise APIError("Patient not found.", status_code=404)
    return patient


def list_patients():
    """List patients with their appointment counts for admin dashboards."""

    patients = db.session.scalars(db.select(Patient).order_by(Patient.created_at.desc())).all()
    results = []
    for patient in patients:
        payload = patient.to_dict()
        payload["appointment_count"] = len(patient.appointments)
        results.append(payload)
    return results
