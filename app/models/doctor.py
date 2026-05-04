"""Doctor domain model."""

from app.extensions import db
from app.models.base import TimestampMixin


class Doctor(TimestampMixin, db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    speciality = db.Column(db.String(80), db.ForeignKey("specialities.name"), nullable=False, index=True)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    phone = db.Column(db.String(20), nullable=False, unique=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    speciality_ref = db.relationship("Speciality", back_populates="doctors", lazy="joined")
    clinic_mappings = db.relationship(
        "DoctorClinicMapping",
        back_populates="doctor",
        cascade="all, delete-orphan",
        lazy="select",
    )
    rosters = db.relationship("DoctorRoster", back_populates="doctor", cascade="all, delete-orphan", lazy="select")
    leaves = db.relationship("DoctorLeave", back_populates="doctor", cascade="all, delete-orphan", lazy="select")
    appointments = db.relationship("Appointment", back_populates="doctor", lazy="select")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "speciality": self.speciality,
            "email": self.email,
            "phone": self.phone,
            "is_admin": self.is_admin,
        }
