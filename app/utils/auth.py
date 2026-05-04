"""Authentication helpers and role guards."""

from functools import wraps

from flask import jsonify, request, session


def login_user(role, username, display_name):
    """Persist a lightweight authenticated session."""

    session["auth_user"] = {
        "role": role,
        "username": username,
        "display_name": display_name,
    }


def logout_user():
    """Clear the current authenticated session."""

    session.pop("auth_user", None)


def get_current_user():
    """Return the current session user payload."""

    return session.get("auth_user")


def require_roles(*roles):
    """Restrict a view to one or more application roles."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            auth_user = get_current_user()
            if not auth_user:
                return jsonify({"message": "Authentication required."}), 401
            if roles and auth_user["role"] not in roles:
                return jsonify({"message": "You do not have permission to access this resource."}), 403
            return view_func(*args, **kwargs)

        return wrapped

    return decorator
