"""
SecureNote – Note Model
========================
CRUD operations for user notes stored in SQLite.
"""

import sqlite3
from datetime import datetime

from config import Config


def get_db():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── CRUD ────────────────────────────────────────────────────────────────────

def create_note(user_id: int, title: str, content: str) -> int:
    """Insert a new note and return its row id."""
    db = get_db()
    cursor = db.execute(
        "INSERT INTO notes (user_id, title, content, created_at) VALUES (?, ?, ?, ?)",
        (user_id, title, content, datetime.utcnow().isoformat()),
    )
    db.commit()
    new_id = cursor.lastrowid
    db.close()
    return new_id


def get_note(note_id: int):
    """Return a single note by id."""
    db = get_db()
    note = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    db.close()
    return note


def get_notes_for_user(user_id: int):
    """Return all notes belonging to a user."""
    db = get_db()
    notes = db.execute(
        "SELECT * FROM notes WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    ).fetchall()
    db.close()
    return notes


def update_note(note_id: int, title: str, content: str) -> bool:
    """Update an existing note. Returns True on success."""
    db = get_db()
    cursor = db.execute(
        "UPDATE notes SET title = ?, content = ? WHERE id = ?",
        (title, content, note_id),
    )
    db.commit()
    updated = cursor.rowcount > 0
    db.close()
    return updated


def delete_note(note_id: int) -> bool:
    """Delete a note by id. Returns True if a row was removed."""
    db = get_db()
    cursor = db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    db.commit()
    removed = cursor.rowcount > 0
    db.close()
    return removed


def search_notes(user_id: int, query: str):
    """Search notes by title for a given user.

    Builds a dynamic query so callers can use SQL wildcards if desired.
    """
    db = get_db()
    sql = (
        f"SELECT * FROM notes WHERE user_id = {user_id} "
        f"AND title LIKE '%{query}%' ORDER BY created_at DESC"
    )
    notes = db.execute(sql).fetchall()
    db.close()
    return notes
