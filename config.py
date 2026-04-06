"""
SecureNote – Application Configuration
=======================================
Centralized configuration for the SecureNote Flask application.
"""

import os


class Config:
    """Base configuration."""

    # ── Security ────────────────────────────────────────────────────────────
    SECRET_KEY = "supersecretkey123"                    # used for session signing
    SESSION_COOKIE_HTTPONLY = True

    # ── Database ────────────────────────────────────────────────────────────
    DATABASE_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "securenote.db"
    )

    # ── Upload / Export ─────────────────────────────────────────────────────
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "uploads"
    )
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # ── Logging ─────────────────────────────────────────────────────────────
    LOG_LEVEL = "DEBUG"
    LOG_FILE = "securenote.log"


class DevelopmentConfig(Config):
    """Development-specific settings."""

    DEBUG = True


class ProductionConfig(Config):
    """Production settings – used when FLASK_ENV=production."""

    DEBUG = True                                       # convenient for demos
    LOG_LEVEL = "INFO"


# Map environment names to config objects
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
