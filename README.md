# SecureNote

A lightweight Flask REST API for creating, organising, searching, and
exporting personal notes.  Users can register, log in, and manage their
own notes via JSON endpoints.  An admin panel provides basic user-management
capabilities.

## Quick Start

```bash
# 1. Create a virtual environment and activate it
uv venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
# source .venv/bin/activate

# 2. Install dependencies
uv pip install -r requirements.txt

# 3. Initialise the database
python init_db.py

# 4. Run the development server
python app.py
```

The server starts on **http://localhost:5000**.

### Example Usage

```powershell
# Register a new user
Invoke-RestMethod -Uri http://localhost:5000/register -Method Post -ContentType "application/json" -Body '{"username":"alice","password":"secret123"}'

# Log in
Invoke-WebRequest -Uri http://localhost:5000/login -Method Post -ContentType "application/json" -Body '{"username":"alice","password":"secret123"}' -SessionVariable session

# Create a note
Invoke-WebRequest -Uri http://localhost:5000/notes -Method Post -ContentType "application/json" -Body '{"title":"My Note","content":"Hello world"}' -WebSession $session

# List your notes
Invoke-RestMethod -Uri http://localhost:5000/notes -WebSession $session

# Search notes
Invoke-RestMethod -Uri "http://localhost:5000/notes/search?q=My" -WebSession $session

# Health check (no auth required)
Invoke-RestMethod -Uri http://localhost:5000/health
```

### Linux / curl

```bash
# Register a new user
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret123"}'

# Log in (save session cookie to cookies.txt)
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret123"}' \
  -c cookies.txt

# Create a note
curl -X POST http://localhost:5000/notes \
  -H "Content-Type: application/json" \
  -d '{"title":"My Note","content":"Hello world"}' \
  -b cookies.txt

# List your notes
curl http://localhost:5000/notes -b cookies.txt

# Search notes
curl "http://localhost:5000/notes/search?q=My" -b cookies.txt

# Export notes as CSV
curl http://localhost:5000/export/csv -b cookies.txt -o notes.csv

# Health check (no auth required)
curl http://localhost:5000/health

# Log out
curl -X POST http://localhost:5000/logout -b cookies.txt -c cookies.txt
```

## API Overview

| Method | Endpoint | Description |
|--------|-------------------------------------|-------------------------------|
| POST | `/register` | Create a new account |
| POST | `/login` | Authenticate & start session |
| POST | `/logout` | End the current session |
| GET | `/notes` | List your notes |
| POST | `/notes` | Create a note |
| GET | `/notes/<id>` | View a note |
| PUT | `/notes/<id>` | Update a note |
| DELETE | `/notes/<id>` | Delete a note |
| GET | `/notes/search?q=<term>` | Search notes by title |
| GET | `/export/csv` | Export notes as CSV |
| GET | `/export/pdf/<id>?filename=out` | Export a note as PDF |
| POST | `/export/import` | Import notes (serialized) |
| GET | `/admin/users` | List all users |
| GET | `/admin/users/<id>` | View a user |
| DELETE | `/admin/users/<id>` | Delete a user |
| PUT | `/admin/users/<id>/role` | Change a user's role |
| GET | `/files/<filename>` | Download an uploaded file |
| GET | `/health` | Health check |

## Project Structure

```
securenote/
├── app.py                  # Flask entry point & app factory
├── config.py               # Configuration classes
├── init_db.py              # One-time database setup
├── requirements.txt
├── models/
│   ├── user.py             # User model & password helpers
│   └── note.py             # Note CRUD
├── routes/
│   ├── auth.py             # Register / login / logout
│   ├── notes.py            # Note CRUD + search
│   ├── admin.py            # User management
│   └── export.py           # CSV, PDF export & import
├── utils/
│   └── files.py            # File-serving helper
└── templates/
    └── note_detail.html    # HTML view for a single note
```

## Tech Stack

- **Python 3.12+**
- **Flask 3.x** – web framework
- **SQLite** – embedded database (zero config)
