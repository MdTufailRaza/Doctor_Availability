"""Clinic domain model."""

from app.extensions import db
from app.models.base import TimestampMixin


class Clinic(TimestampMixin, db.Model):
    __tablename__ = "clinics"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(255), nullable=False)

    __table_args__ = (db.UniqueConstraint("name", "location", name="uq_clinic_name_location"),)

    doctor_mappings = db.relationship(
        "DoctorClinicMapping",
        back_populates="clinic",
        cascade="all, delete-orphan",
        lazy="select",
    )
    rosters = db.relationship("DoctorRoster", back_populates="clinic", cascade="all, delete-orphan", lazy="select")
    appointments = db.relationship("Appointment", back_populates="clinic", lazy="select")

    def to_dict(self, include_doctors=False):
        payload = {"id": self.id, "name": self.name, "location": self.location}
        if include_doctors:
            payload["doctors"] = [mapping.doctor.to_dict() for mapping in self.doctor_mappings]
        return payload
