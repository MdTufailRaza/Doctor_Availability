"""Patient domain model."""

from app.extensions import db
from app.models.base import TimestampMixin


class Patient(TimestampMixin, db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    contact = db.Column(db.String(30), nullable=False, unique=True, index=True)

    appointments = db.relationship("Appointment", back_populates="patient", lazy="select")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "contact": self.contact}
