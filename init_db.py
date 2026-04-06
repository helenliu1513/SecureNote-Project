"""
SecureNote – Database Initialisation
======================================
Run this script once to create the SQLite tables.

    python init_db.py
"""

import os
import sqlite3
from config import Config


def init_database():
    """Create the users and notes tables if they don't exist."""
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            role          TEXT    NOT NULL DEFAULT 'user'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            title      TEXT    NOT NULL,
            content    TEXT    NOT NULL DEFAULT '',
            created_at TEXT    NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database initialised at {Config.DATABASE_PATH}")


if __name__ == "__main__":
    init_database()
