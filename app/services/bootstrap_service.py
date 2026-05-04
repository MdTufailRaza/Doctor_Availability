"""Reference data bootstrap utilities."""

from sqlalchemy import inspect, text

from app.extensions import db
from app.models import Speciality
from app.utils.constants import DEFAULT_SPECIALITIES


def ensure_schema_compatibility():
    """Apply lightweight SQLite-safe schema upgrades for local development."""

    inspector = inspect(db.engine)
    if "appointments" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("appointments")}
    statements = []

    if "is_confirmed" not in columns:
        statements.append("ALTER TABLE appointments ADD COLUMN is_confirmed BOOLEAN NOT NULL DEFAULT 0")
    if "confirmed_at" not in columns:
        statements.append("ALTER TABLE appointments ADD COLUMN confirmed_at DATETIME")

    if statements:
        with db.engine.begin() as connection:
            for statement in statements:
                connection.execute(text(statement))


def bootstrap_reference_data():
    """Ensure required lookup data exists."""

    for name in DEFAULT_SPECIALITIES:
        speciality = db.session.get(Speciality, name)
        if not speciality:
            db.session.add(Speciality(name=name, description=f"{name} speciality"))
    db.session.commit()
