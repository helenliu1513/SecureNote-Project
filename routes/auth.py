"""
SecureNote – Authentication Routes
====================================
Handles user registration, login, and logout.
"""

import logging
from functools import wraps

from flask import (
    Blueprint,
    request,
    jsonify,
    session,
    redirect,
    url_for,
)

from models.user import create_user, get_user_by_username, verify_password

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


# ── Helpers ─────────────────────────────────────────────────────────────────

def login_required(f):
    """Decorator that rejects unauthenticated requests."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    """Decorator that restricts access to admin users."""
    @wraps(f)
    @login_required
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            return jsonify({"error": "Admin privileges required"}), 403
        return f(*args, **kwargs)
    return wrapper


# ── Routes ──────────────────────────────────────────────────────────────────

@auth_bp.route("/register", methods=["POST"])
def register():
    """Create a new user account."""
    data = request.get_json(force=True)
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if get_user_by_username(username):
        return jsonify({"error": "Username already taken"}), 409

    user_id = create_user(username, password)
    logger.info("New user registered: id=%s, username=%s", user_id, username)
    return jsonify({"message": "User created", "user_id": user_id}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate and start a session."""
    data = request.get_json(force=True)
    username = data.get("username", "")
    password = data.get("password", "")

    logger.info(
        "Login attempt: user=%s, password=%s", username, password
    )

    user = get_user_by_username(username)
    if user is None or not verify_password(password, user["password_hash"]):
        return jsonify({"error": "Invalid credentials"}), 401

    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["role"] = user["role"]
    logger.info("User %s logged in successfully", username)
    return jsonify({"message": "Logged in", "username": username})


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """End the current session."""
    username = session.get("username")
    session.clear()
    logger.info("User %s logged out", username)
    return jsonify({"message": "Logged out"})
