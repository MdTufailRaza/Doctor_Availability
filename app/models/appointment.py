"""Appointment domain model."""

from datetime import datetime
from enum import Enum

from sqlalchemy import Enum as SqlEnum

from app.extensions import db
from app.models.base import TimestampMixin
from app.utils.date_utils import serialize_date, serialize_datetime, serialize_time


class AppointmentStatus(str, Enum):
    BOOKED = "BOOKED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NOSHOW = "NOSHOW"


class Appointment(TimestampMixin, db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False, index=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey("clinics.id"), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    time = db.Column(db.Time, nullable=False)
    is_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(
        SqlEnum(AppointmentStatus, native_enum=False, validate_strings=True),
        nullable=False,
        default=AppointmentStatus.BOOKED,
    )

    __table_args__ = (db.Index("ix_appointment_doctor_schedule", "doctor_id", "clinic_id", "date", "time"),)

    patient = db.relationship("Patient", back_populates="appointments", lazy="joined")
    doctor = db.relationship("Doctor", back_populates="appointments", lazy="joined")
    clinic = db.relationship("Clinic", back_populates="appointments", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "patient": self.patient.to_dict(),
            "doctor": self.doctor.to_dict(),
            "clinic": self.clinic.to_dict(),
            "date": serialize_date(self.date),
            "time": serialize_time(self.time),
            "is_confirmed": self.is_confirmed,
            "confirmed_at": serialize_datetime(self.confirmed_at),
            "status": self.status.value if hasattr(self.status, "value") else str(self.status),
        }
