"""Flask application factory."""

from pathlib import Path

from flask import Flask, render_template

from app.config import Config
from app.extensions import cors, db
from app.routes import (
    admin_bp,
    auth_bp,
    appointment_bp,
    availability_bp,
    clinic_bp,
    doctor_bp,
    leave_bp,
    patient_bp,
    report_bp,
    roster_bp,
    web_bp,
)
from app.services.bootstrap_service import bootstrap_reference_data, ensure_schema_compatibility
from app.utils.errors import register_error_handlers


def create_app(config_class=Config):
    """Create and configure the Flask application."""

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    cors.init_app(app)
    register_error_handlers(app)

    app.register_blueprint(web_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(clinic_bp)
    app.register_blueprint(roster_bp)
    app.register_blueprint(leave_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(availability_bp)
    app.register_blueprint(appointment_bp)

    with app.app_context():
        db.create_all()
        ensure_schema_compatibility()
        bootstrap_reference_data()

    return app
