"""Domain constants used across modules."""

ALLOWED_LEAVE_REASONS = {
    "VACATION",
    "SICK",
    "TRAINING",
    "CONFERENCE",
    "EMERGENCY",
}

DAYS_OF_WEEK = {
    "MONDAY",
    "TUESDAY",
    "WEDNESDAY",
    "THURSDAY",
    "FRIDAY",
    "SATURDAY",
    "SUNDAY",
}

DEFAULT_SPECIALITIES = [
    "Cardiology",
    "Dermatology",
    "General Physician",
    "Gynecology",
    "Neurology",
    "Orthopedics",
    "Pediatrics",
    "Radiology",
]

FINAL_APPOINTMENT_STATUSES = {"COMPLETED", "CANCELLED", "NOSHOW"}
