"""Validation and normalization helpers."""

import re

from app.utils.constants import DAYS_OF_WEEK
from app.utils.errors import APIError


EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def ensure_required_fields(payload, fields):
    """Validate required fields exist and are not blank."""

    missing = [field for field in fields if not str(payload.get(field, "")).strip()]
    if missing:
        raise APIError(
            f"Missing required field(s): {', '.join(missing)}.",
            status_code=400,
        )


def validate_email(email):
    """Validate email format."""

    if not EMAIL_REGEX.match(email or ""):
        raise APIError("Invalid email format.", status_code=400)


def normalize_text(value):
    """Normalize free-form text input."""

    return " ".join(str(value or "").strip().split())


def normalize_speciality(value):
    """Normalize speciality names for consistent storage."""

    return normalize_text(value).title()


def normalize_day(value):
    """Normalize weekday values to uppercase constants."""

    normalized = normalize_text(value).upper()
    if normalized not in DAYS_OF_WEEK:
        raise APIError(
            f"Invalid day. Supported values: {', '.join(sorted(DAYS_OF_WEEK))}.",
            status_code=400,
        )
    return normalized
