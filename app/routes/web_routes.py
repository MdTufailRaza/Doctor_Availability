"""HTML page routes for login and dashboards."""

from flask import Blueprint, redirect, render_template, session, url_for

from app.utils.auth import get_current_user


web_bp = Blueprint("web_bp", __name__)


def _dashboard_endpoint_for_role(role):
    return "web_bp.admin_dashboard" if role == "admin" else "web_bp.user_dashboard"


@web_bp.get("/")
def index():
    auth_user = get_current_user()
    if auth_user:
        return redirect(url_for(_dashboard_endpoint_for_role(auth_user["role"])))
    return render_template("login_portal.html")


@web_bp.get("/login/user")
def user_login():
    auth_user = get_current_user()
    if auth_user and auth_user["role"] == "user":
        return redirect(url_for("web_bp.user_dashboard"))
    return render_template("user_login.html")


@web_bp.get("/login/admin")
def admin_login():
    auth_user = get_current_user()
    if auth_user and auth_user["role"] == "admin":
        return redirect(url_for("web_bp.admin_dashboard"))
    return render_template("admin_login.html")


@web_bp.get("/dashboard/user")
def user_dashboard():
    auth_user = get_current_user()
    if not auth_user:
        return redirect(url_for("web_bp.user_login"))
    if auth_user["role"] != "user":
        return redirect(url_for("web_bp.admin_dashboard"))
    return render_template("user_dashboard.html", auth_user=auth_user)


@web_bp.get("/dashboard/admin")
def admin_dashboard():
    auth_user = get_current_user()
    if not auth_user:
        return redirect(url_for("web_bp.admin_login"))
    if auth_user["role"] != "admin":
        return redirect(url_for("web_bp.user_dashboard"))
    return render_template("admin_dashboard.html", auth_user=auth_user)
