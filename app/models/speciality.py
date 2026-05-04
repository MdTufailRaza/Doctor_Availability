"""Speciality reference entity."""

from app.extensions import db
from app.models.base import TimestampMixin


class Speciality(TimestampMixin, db.Model):
    __tablename__ = "specialities"

    name = db.Column(db.String(80), primary_key=True)
    description = db.Column(db.String(255), nullable=True)

    doctors = db.relationship("Doctor", back_populates="speciality_ref", lazy="select")

    def to_dict(self):
        return {"name": self.name, "description": self.description}
