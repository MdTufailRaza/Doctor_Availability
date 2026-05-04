"""Session authentication service."""

from flask import current_app

from app.utils.errors import APIError


def authenticate(role, username, password):
    """Validate demo credentials for the requested role."""

    credentials_map = {
        "user": current_app.config["USER_CREDENTIALS"],
        "admin": current_app.config["ADMIN_CREDENTIALS"],
    }

    if role not in credentials_map:
        raise APIError("Unsupported role.", status_code=400)

    expected = credentials_map[role]
    if username != expected["username"] or password != expected["password"]:
        raise APIError("Invalid username or password.", status_code=401)

    return {
        "role": role,
        "username": expected["username"],
        "display_name": expected["display_name"],
    }
