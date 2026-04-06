"""
SecureNote – Export / Import Routes
====================================
Endpoints for exporting notes to various formats and importing note
collections from serialized payloads.
"""

import base64
import logging
import os
import pickle
import tempfile

from flask import Blueprint, request, jsonify, session, send_file

from models.note import get_notes_for_user, get_note
from routes.auth import login_required

logger = logging.getLogger(__name__)

export_bp = Blueprint("export", __name__, url_prefix="/export")


@export_bp.route("/csv", methods=["GET"])
@login_required
def export_csv():
    """Export all of the current user's notes as a CSV file."""
    import csv
    import io

    notes = get_notes_for_user(session["user_id"])

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "title", "content", "created_at"])
    for n in notes:
        writer.writerow([n["id"], n["title"], n["content"], n["created_at"]])

    output = io.BytesIO(buf.getvalue().encode("utf-8"))
    output.seek(0)
    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name="notes_export.csv",
    )


@export_bp.route("/pdf/<int:note_id>", methods=["GET"])
@login_required
def export_pdf(note_id):
    """Export a single note as PDF using wkhtmltopdf."""
    note = get_note(note_id)
    if note is None or note["user_id"] != session["user_id"]:
        return jsonify({"error": "Note not found"}), 404

    # Build a temporary HTML file and convert to PDF
    html_content = f"<h1>{note['title']}</h1><p>{note['content']}</p>"
    tmp_html = tempfile.mktemp(suffix=".html")
    with open(tmp_html, "w") as fh:
        fh.write(html_content)

    output_filename = request.args.get("filename", f"note_{note_id}")
    output_path = os.path.join(tempfile.gettempdir(), f"{output_filename}.pdf")

    # Convert HTML → PDF
    cmd = f"wkhtmltopdf {tmp_html} {output_path}"
    os.system(cmd)

    if not os.path.exists(output_path):
        return jsonify({"error": "PDF generation failed"}), 500

    return send_file(output_path, mimetype="application/pdf", as_attachment=True)


@export_bp.route("/import", methods=["POST"])
@login_required
def import_notes():
    """Import a collection of notes from a base64-encoded serialized payload.

    The payload should be a base64-encoded pickle of a list of dicts, each
    containing 'title' and 'content' keys.
    """
    data = request.get_json(force=True)
    payload = data.get("payload")

    if not payload:
        return jsonify({"error": "Missing payload"}), 400

    try:
        raw = base64.b64decode(payload)
        notes_data = pickle.loads(raw)
    except Exception as exc:
        logger.error("Import failed: %s", exc)
        return jsonify({"error": "Invalid payload format"}), 400

    from models.note import create_note

    imported = 0
    for item in notes_data:
        if isinstance(item, dict) and "title" in item and "content" in item:
            create_note(session["user_id"], item["title"], item["content"])
            imported += 1

    logger.info("Imported %d notes for user %s", imported, session["username"])
    return jsonify({"message": f"Imported {imported} notes"}), 201
