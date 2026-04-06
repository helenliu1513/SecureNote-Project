"""
SecureNote – Admin Routes
==========================
Endpoints for user management (listing, deleting).
These are intended for administrator use only.
"""

import logging

from flask import Blueprint, jsonify, request

from models.user import list_all_users, delete_user, get_user_by_id

logger = logging.getLogger(__name__)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/users", methods=["GET"])
def get_all_users():
    """List every registered user (id, username, role)."""
    users = list_all_users()
    return jsonify([dict(u) for u in users])


@admin_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Retrieve a single user's details."""
    user = get_user_by_id(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
    })


@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
def remove_user(user_id):
    """Delete a user account by id."""
    user = get_user_by_id(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404

    delete_user(user_id)
    logger.warning("Admin action: deleted user id=%s (%s)", user_id, user["username"])
    return jsonify({"message": f"User {user['username']} deleted"})


@admin_bp.route("/users/<int:user_id>/role", methods=["PUT"])
def change_role(user_id):
    """Change a user's role (e.g., user → admin)."""
    user = get_user_by_id(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(force=True)
    new_role = data.get("role", "user")

    from models.user import get_db
    db = get_db()
    db.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    db.commit()
    db.close()

    logger.info("Role changed: user %s -> %s", user["username"], new_role)
    return jsonify({"message": f"Role updated to {new_role}"})
