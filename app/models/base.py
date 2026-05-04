"""Base model mixins."""

from datetime import datetime

from app.extensions import db


class TimestampMixin:
    """Adds created/updated timestamps to records."""

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
