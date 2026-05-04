"""Model exports."""

from app.models.appointment import Appointment, AppointmentStatus
from app.models.clinic import Clinic
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.schedule import DoctorClinicMapping, DoctorLeave, DoctorRoster
from app.models.speciality import Speciality

__all__ = [
    "Appointment",
    "AppointmentStatus",
    "Clinic",
    "Doctor",
    "DoctorClinicMapping",
    "DoctorLeave",
    "DoctorRoster",
    "Patient",
    "Speciality",
]
