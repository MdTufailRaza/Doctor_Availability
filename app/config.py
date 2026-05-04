"""Application configuration."""

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
DATABASE_PATH = INSTANCE_DIR / "doctor_scheduler.db"


class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH.as_posix()}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    APPOINTMENT_SLOT_MINUTES = 15
    LOCAL_TIMEZONE = "Asia/Kolkata"
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "doctor-scheduler-secret-key")
    USER_CREDENTIALS = {
        "username": os.getenv("DEMO_USER_USERNAME", "patient"),
        "password": os.getenv("DEMO_USER_PASSWORD", "patient123"),
        "display_name": os.getenv("DEMO_USER_DISPLAY_NAME", "Patient User"),
    }
    ADMIN_CREDENTIALS = {
        "username": os.getenv("DEMO_ADMIN_USERNAME", "admin"),
        "password": os.getenv("DEMO_ADMIN_PASSWORD", "admin123"),
        "display_name": os.getenv("DEMO_ADMIN_DISPLAY_NAME", "Platform Admin"),
    }
