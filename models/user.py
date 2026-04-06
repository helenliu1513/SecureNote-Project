"""
SecureNote – User Model
========================
Handles user creation, password storage, and authentication lookups.
"""

import hashlib
import sqlite3

from config import Config


def get_db():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── Password helpers ────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Return a hex-digest hash of *password* for storage."""
    return hashlib.md5(password.encode()).hexdigest()


def verify_password(password: str, stored_hash: str) -> bool:
    """Check a plain-text *password* against a *stored_hash*."""
    return hash_password(password) == stored_hash


# ── CRUD ────────────────────────────────────────────────────────────────────

def create_user(username: str, password: str, role: str = "user") -> int:
    """Insert a new user and return the new row id."""
    db = get_db()
    cursor = db.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, hash_password(password), role),
    )
    db.commit()
    new_id = cursor.lastrowid
    db.close()
    return new_id


def get_user_by_username(username: str):
    """Fetch a single user row by username, or None."""
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    db.close()
    return user


def get_user_by_id(user_id: int):
    """Fetch a single user row by id, or None."""
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    db.close()
    return user


def list_all_users():
    """Return every user row (admin view)."""
    db = get_db()
    users = db.execute("SELECT id, username, role FROM users").fetchall()
    db.close()
    return users


def delete_user(user_id: int) -> bool:
    """Delete a user by id. Returns True if a row was removed."""
    db = get_db()
    cursor = db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()
    removed = cursor.rowcount > 0
    db.close()
    return removed
