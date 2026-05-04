"""Route package exports."""

from app.routes.admin_routes import admin_bp
from app.routes.auth_routes import auth_bp
from app.routes.appointment_routes import appointment_bp
from app.routes.availability_routes import availability_bp
from app.routes.clinic_routes import clinic_bp
from app.routes.doctor_routes import doctor_bp
from app.routes.leave_routes import leave_bp
from app.routes.patient_routes import patient_bp
from app.routes.report_routes import report_bp
from app.routes.roster_routes import roster_bp
from app.routes.web_routes import web_bp

__all__ = [
    "admin_bp",
    "auth_bp",
    "appointment_bp",
    "availability_bp",
    "clinic_bp",
    "doctor_bp",
    "leave_bp",
    "patient_bp",
    "report_bp",
    "roster_bp",
    "web_bp",
]
