"""Scheduling and leave-related models."""

from app.extensions import db
from app.models.base import TimestampMixin
from app.utils.date_utils import serialize_date, serialize_time


class DoctorClinicMapping(TimestampMixin, db.Model):
    __tablename__ = "doctor_clinic_mapping"

    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), primary_key=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey("clinics.id"), primary_key=True)

    doctor = db.relationship("Doctor", back_populates="clinic_mappings", lazy="joined")
    clinic = db.relationship("Clinic", back_populates="doctor_mappings", lazy="joined")

    def to_dict(self):
        return {
            "doctor_id": self.doctor_id,
            "clinic_id": self.clinic_id,
            "doctor_name": self.doctor.name,
            "clinic_name": self.clinic.name,
        }


class DoctorLeave(TimestampMixin, db.Model):
    __tablename__ = "doctor_leave"

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False, index=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(50), nullable=False)

    __table_args__ = (db.CheckConstraint("start_date <= end_date", name="ck_doctor_leave_dates"),)

    doctor = db.relationship("Doctor", back_populates="leaves", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "doctor_id": self.doctor_id,
            "doctor_name": self.doctor.name,
            "start_date": serialize_date(self.start_date),
            "end_date": serialize_date(self.end_date),
            "reason": self.reason,
        }


class DoctorRoster(TimestampMixin, db.Model):
    __tablename__ = "doctor_roster"

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False, index=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey("clinics.id"), nullable=False, index=True)
    day = db.Column(db.String(15), nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    __table_args__ = (
        db.CheckConstraint("start_time < end_time", name="ck_doctor_roster_times"),
        db.UniqueConstraint(
            "doctor_id",
            "clinic_id",
            "day",
            "start_time",
            "end_time",
            name="uq_doctor_roster_slot",
        ),
    )

    doctor = db.relationship("Doctor", back_populates="rosters", lazy="joined")
    clinic = db.relationship("Clinic", back_populates="rosters", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "doctor_id": self.doctor_id,
            "doctor_name": self.doctor.name,
            "clinic_id": self.clinic_id,
            "clinic_name": self.clinic.name,
            "day": self.day,
            "start_time": serialize_time(self.start_time),
            "end_time": serialize_time(self.end_time),
        }
