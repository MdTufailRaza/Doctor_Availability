"""Seed the database with demo data."""

from app import create_app
from app.extensions import db
from app.models import Appointment, AppointmentStatus, Clinic, Doctor, DoctorClinicMapping, DoctorLeave, DoctorRoster, Patient
from app.services.bootstrap_service import bootstrap_reference_data
from app.utils.date_utils import parse_date, parse_time


app = create_app()


def get_or_create(model, defaults=None, **lookup):
    instance = db.session.scalar(db.select(model).filter_by(**lookup))
    if instance:
        for key, value in (defaults or {}).items():
            setattr(instance, key, value)
        return instance
    params = {**lookup, **(defaults or {})}
    instance = model(**params)
    db.session.add(instance)
    db.session.flush()
    return instance


with app.app_context():
    db.create_all()
    bootstrap_reference_data()

    gyne = get_or_create(
        Doctor,
        name="Dr. Ananya Sen",
        speciality="Gynecology",
        email="ananya.sen@hospital.com",
        phone="9000000001",
        is_admin=True,
    )
    pediatrician = get_or_create(
        Doctor,
        name="Dr. Ravi Mehta",
        speciality="Pediatrics",
        email="ravi.mehta@hospital.com",
        phone="9000000002",
    )
    physician = get_or_create(
        Doctor,
        name="Dr. Kavita Iyer",
        speciality="General Physician",
        email="kavita.iyer@hospital.com",
        phone="9000000003",
    )
    cardiologist = get_or_create(
        Doctor,
        name="Dr. Arjun Khanna",
        speciality="Cardiology",
        email="arjun.khanna@hospital.com",
        phone="9000000004",
    )

    clinic_a = get_or_create(Clinic, name="City Care Clinic", location="Park Street")
    clinic_b = get_or_create(Clinic, name="Sunrise Health Center", location="Salt Lake")

    for doctor, clinic in [
        (gyne, clinic_a),
        (gyne, clinic_b),
        (pediatrician, clinic_a),
        (physician, clinic_a),
        (physician, clinic_b),
        (cardiologist, clinic_b),
    ]:
        get_or_create(DoctorClinicMapping, doctor_id=doctor.id, clinic_id=clinic.id)

    roster_data = [
        {"doctor_id": gyne.id, "clinic_id": clinic_a.id, "day": "MONDAY", "start_time": parse_time("09:00"), "end_time": parse_time("13:00")},
        {"doctor_id": gyne.id, "clinic_id": clinic_b.id, "day": "WEDNESDAY", "start_time": parse_time("10:00"), "end_time": parse_time("14:00")},
        {"doctor_id": pediatrician.id, "clinic_id": clinic_a.id, "day": "TUESDAY", "start_time": parse_time("09:00"), "end_time": parse_time("12:00")},
        {"doctor_id": pediatrician.id, "clinic_id": clinic_a.id, "day": "THURSDAY", "start_time": parse_time("14:00"), "end_time": parse_time("18:00")},
        {"doctor_id": physician.id, "clinic_id": clinic_a.id, "day": "MONDAY", "start_time": parse_time("08:00"), "end_time": parse_time("12:00")},
        {"doctor_id": physician.id, "clinic_id": clinic_b.id, "day": "FRIDAY", "start_time": parse_time("12:00"), "end_time": parse_time("18:00")},
        {"doctor_id": cardiologist.id, "clinic_id": clinic_b.id, "day": "SATURDAY", "start_time": parse_time("09:00"), "end_time": parse_time("13:00")},
    ]

    for roster in roster_data:
        get_or_create(
            DoctorRoster,
            doctor_id=roster["doctor_id"],
            clinic_id=roster["clinic_id"],
            day=roster["day"],
            start_time=roster["start_time"],
            end_time=roster["end_time"],
        )

    get_or_create(
        DoctorLeave,
        doctor_id=physician.id,
        start_date=parse_date("2026-04-27"),
        end_date=parse_date("2026-04-28"),
        reason="TRAINING",
    )

    patient_1 = get_or_create(Patient, name="Neha Sharma", contact="8800000001")
    patient_2 = get_or_create(Patient, name="Amit Das", contact="8800000002")

    get_or_create(
        Appointment,
        defaults={
            "is_confirmed": False,
            "status": AppointmentStatus.BOOKED,
        },
        patient_id=patient_1.id,
        doctor_id=pediatrician.id,
        clinic_id=clinic_a.id,
        date=parse_date("2026-04-23"),
        time=parse_time("14:00"),
    )
    get_or_create(
        Appointment,
        defaults={
            "is_confirmed": True,
            "status": AppointmentStatus.COMPLETED,
        },
        patient_id=patient_2.id,
        doctor_id=physician.id,
        clinic_id=clinic_b.id,
        date=parse_date("2026-04-24"),
        time=parse_time("12:00"),
    )

    db.session.commit()
    print("Seed data loaded successfully.")
