"""
SecureNote – Notes Routes
==========================
CRUD endpoints and search for user notes.
"""

import logging

from flask import Blueprint, request, jsonify, session, render_template

from models.note import (
    create_note,
    get_note,
    get_notes_for_user,
    update_note,
    delete_note,
    search_notes,
)
from routes.auth import login_required

logger = logging.getLogger(__name__)

notes_bp = Blueprint("notes", __name__)


# ── List & Search ──────────────────────────────────────────────────────────

@notes_bp.route("/notes", methods=["GET"])
@login_required
def list_notes():
    """Return all notes for the logged-in user."""
    user_id = session["user_id"]
    notes = get_notes_for_user(user_id)
    return jsonify([dict(n) for n in notes])


@notes_bp.route("/notes/search", methods=["GET"])
@login_required
def search():
    """Full-text search across note titles for the current user."""
    user_id = session["user_id"]
    query = request.args.get("q", "")
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    results = search_notes(user_id, query)
    return jsonify([dict(n) for n in results])


# ── Create ──────────────────────────────────────────────────────────────────

@notes_bp.route("/notes", methods=["POST"])
@login_required
def new_note():
    """Create a new note."""
    data = request.get_json(force=True)
    title = data.get("title", "").strip()
    content = data.get("content", "")

    if not title:
        return jsonify({"error": "Title is required"}), 400

    note_id = create_note(session["user_id"], title, content)
    logger.info("Note created: id=%s by user=%s", note_id, session["username"])
    return jsonify({"message": "Note created", "note_id": note_id}), 201


# ── Read ────────────────────────────────────────────────────────────────────

@notes_bp.route("/notes/<int:note_id>", methods=["GET"])
@login_required
def view_note(note_id):
    """View a single note. Renders HTML when Accept header includes text/html."""
    note = get_note(note_id)
    if note is None or note["user_id"] != session["user_id"]:
        return jsonify({"error": "Note not found"}), 404

    if "text/html" in request.headers.get("Accept", ""):
        return render_template("note_detail.html", note=dict(note))

    return jsonify(dict(note))


# ── Update ──────────────────────────────────────────────────────────────────

@notes_bp.route("/notes/<int:note_id>", methods=["PUT"])
@login_required
def edit_note(note_id):
    """Update a note's title and/or content."""
    note = get_note(note_id)
    if note is None or note["user_id"] != session["user_id"]:
        return jsonify({"error": "Note not found"}), 404

    data = request.get_json(force=True)
    new_title = data.get("title", note["title"])
    new_content = data.get("content", note["content"])

    update_note(note_id, new_title, new_content)
    logger.info("Note updated: id=%s", note_id)
    return jsonify({"message": "Note updated"})


# ── Delete ──────────────────────────────────────────────────────────────────

@notes_bp.route("/notes/<int:note_id>", methods=["DELETE"])
@login_required
def remove_note(note_id):
    """Delete a note."""
    note = get_note(note_id)
    if note is None or note["user_id"] != session["user_id"]:
        return jsonify({"error": "Note not found"}), 404

    delete_note(note_id)
    logger.info("Note deleted: id=%s", note_id)
    return jsonify({"message": "Note deleted"})
