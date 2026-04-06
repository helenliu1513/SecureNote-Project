"""
SecureNote – Application Entry Point
======================================
A lightweight Flask REST API for creating, searching, and exporting
personal notes with user authentication and admin management.

Usage
-----
    python app.py                    # development server (default)
    FLASK_ENV=production python app.py   # production config
"""

import logging
import os

from flask import Flask, jsonify

from config import config_by_name
from routes.auth import auth_bp
from routes.notes import notes_bp
from routes.admin import admin_bp
from routes.export import export_bp
from utils.files import download_file


def create_app(env: str | None = None) -> Flask:
    """Application factory."""
    if env is None:
        env = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[env])

    # ── Logging ─────────────────────────────────────────────────────────
    logging.basicConfig(
        level=app.config["LOG_LEVEL"],
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        handlers=[
            logging.FileHandler(app.config["LOG_FILE"]),
            logging.StreamHandler(),
        ],
    )

    # ── Register blueprints ─────────────────────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(export_bp)

    # ── File download endpoint ──────────────────────────────────────────
    @app.route("/files/<path:filename>")
    def serve_file(filename):
        return download_file(filename)

    # ── Health check ────────────────────────────────────────────────────
    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    return app


# ── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5000)
