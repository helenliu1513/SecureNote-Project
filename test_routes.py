"""
SecureNote - End-to-End Route Tests
====================================
Run with:  python test_routes.py
Requires the server to be running on http://localhost:5000.
"""

import json
import requests
import base64
import pickle
import sys
import time

BASE = "http://localhost:5000"
session = requests.Session()

passed = 0
failed = 0


def test(name, response, expected_status, check_json_key=None):
    global passed, failed
    ok = response.status_code == expected_status
    if check_json_key and ok:
        try:
            ok = check_json_key in response.json()
        except Exception:
            ok = False
    status = "PASS" if ok else "FAIL"
    if not ok:
        failed += 1
        print(f"  [{status}] {name}: got {response.status_code}, expected {expected_status}")
        try:
            print(f"         Body: {response.text[:200]}")
        except Exception:
            pass
    else:
        passed += 1
        print(f"  [{status}] {name}")


def safe_request(method, url, retries=2, delay=2, **kwargs):
    """Make a request with retry logic for connection errors."""
    for attempt in range(retries + 1):
        try:
            return method(url, **kwargs)
        except requests.ConnectionError:
            if attempt < retries:
                print(f"         -> Connection refused, retrying in {delay}s...")
                time.sleep(delay)
            else:
                raise


print("=" * 60)
print("SecureNote - Route Tests")
print("=" * 60)

# ── 1. Unauthenticated ──────────────────────────────────────────────────
print("\n[1] Unauthenticated Endpoints")
r = session.get(f"{BASE}/health")
test("GET /health", r, 200, "status")

r = session.post(f"{BASE}/register", json={"username": "alice", "password": "alice123"})
test("POST /register (new user)", r, 201, "user_id")

r = session.post(f"{BASE}/register", json={"username": "alice", "password": "alice123"})
test("POST /register (duplicate)", r, 409)

r = session.post(f"{BASE}/register", json={"username": "", "password": ""})
test("POST /register (empty fields)", r, 400)

# ── 2. Auth Flow ────────────────────────────────────────────────────────
print("\n[2] Authentication Flow")
r = session.post(f"{BASE}/login", json={"username": "alice", "password": "wrong"})
test("POST /login (wrong password)", r, 401)

r = session.post(f"{BASE}/login", json={"username": "alice", "password": "alice123"})
test("POST /login (correct)", r, 200, "username")

# Check that session cookie was set
has_cookie = any(c.name == "session" for c in session.cookies)
print(f"  [{'PASS' if has_cookie else 'FAIL'}] Session cookie present: {has_cookie}")
if has_cookie:
    passed += 1
else:
    failed += 1

# ── 3. Note CRUD ────────────────────────────────────────────────────────
print("\n[3] Note CRUD")
r = session.post(f"{BASE}/notes", json={"title": "First Note", "content": "Hello world"})
test("POST /notes (create)", r, 201, "note_id")
note1_id = r.json().get("note_id")

r = session.post(f"{BASE}/notes", json={"title": "Second Note", "content": "Goodbye"})
test("POST /notes (create #2)", r, 201)
note2_id = r.json().get("note_id")

r = session.post(f"{BASE}/notes", json={"title": "Search Target", "content": "Find me"})
test("POST /notes (create #3)", r, 201)

r = session.get(f"{BASE}/notes")
test("GET /notes (list)", r, 200)
notes = r.json()
print(f"         -> {len(notes)} notes returned")

r = session.get(f"{BASE}/notes/{note1_id}")
test(f"GET /notes/{note1_id} (detail)", r, 200, "title")

r = session.put(f"{BASE}/notes/{note1_id}", json={"title": "Updated Title"})
test(f"PUT /notes/{note1_id} (update)", r, 200)

r = session.delete(f"{BASE}/notes/{note1_id}")
test(f"DELETE /notes/{note1_id}", r, 200)

r = session.get(f"{BASE}/notes/{note1_id}")
test(f"GET /notes/{note1_id} (after delete)", r, 404)

# ── 4. Search ────────────────────────────────────────────────────────────
print("\n[4] Note Search")
r = session.get(f"{BASE}/notes/search", params={"q": "Search"})
test("GET /notes/search?q=Search", r, 200)
results = r.json()
print(f"         -> {len(results)} results")

r = session.get(f"{BASE}/notes/search")
test("GET /notes/search (no q param)", r, 400)

# ── 5. Export ────────────────────────────────────────────────────────────
print("\n[5] Export Endpoints")
r = session.get(f"{BASE}/export/csv")
test("GET /export/csv", r, 200)
print(f"         -> Content-Type: {r.headers.get('Content-Type', 'N/A')}")

r = session.get(f"{BASE}/export/pdf/{note2_id}")
# wkhtmltopdf likely not installed, so 500 is expected
test(f"GET /export/pdf/{note2_id} (may fail if wkhtmltopdf missing)", r, 500)

# Import via pickle (testing the vulnerability works)
payload_data = [{"title": "Imported Note", "content": "Via pickle"}]
encoded = base64.b64encode(pickle.dumps(payload_data)).decode()
r = safe_request(session.post, f"{BASE}/export/import", json={"payload": encoded})
test("POST /export/import (pickle)", r, 201)

r = session.post(f"{BASE}/export/import", json={})
test("POST /export/import (missing payload)", r, 400)

# ── 6. Admin (NO AUTH - vulnerability) ──────────────────────────────────
print("\n[6] Admin Endpoints (unauthenticated)")
admin_session = requests.Session()  # fresh session, no login

r = admin_session.get(f"{BASE}/admin/users")
test("GET /admin/users (no auth)", r, 200)
users = r.json()
print(f"         -> {len(users)} users")

r = admin_session.get(f"{BASE}/admin/users/1")
test("GET /admin/users/1 (no auth)", r, 200, "username")

# Create a disposable user to delete
session.post(f"{BASE}/register", json={"username": "disposable", "password": "delete_me"})
r = admin_session.get(f"{BASE}/admin/users")
disposable_id = None
for u in r.json():
    if u["username"] == "disposable":
        disposable_id = u["id"]

if disposable_id:
    r = admin_session.put(f"{BASE}/admin/users/{disposable_id}/role", json={"role": "admin"})
    test(f"PUT /admin/users/{disposable_id}/role (no auth)", r, 200)

    r = admin_session.delete(f"{BASE}/admin/users/{disposable_id}")
    test(f"DELETE /admin/users/{disposable_id} (no auth)", r, 200)
else:
    print("  [SKIP] Could not find disposable user to test delete")

# ── 7. File Download ────────────────────────────────────────────────────
print("\n[7] File Download")
r = session.get(f"{BASE}/files/nonexistent.txt")
test("GET /files/nonexistent.txt", r, 404)

# ── 8. Auth-required without login ──────────────────────────────────────
print("\n[8] Auth Enforcement")
unauth = requests.Session()
r = unauth.get(f"{BASE}/notes")
test("GET /notes (no auth)", r, 401)

r = unauth.post(f"{BASE}/notes", json={"title": "x", "content": "y"})
test("POST /notes (no auth)", r, 401)

r = unauth.get(f"{BASE}/export/csv")
test("GET /export/csv (no auth)", r, 401)

# ── 9. Logout ────────────────────────────────────────────────────────────
print("\n[9] Logout")
r = session.post(f"{BASE}/logout")
test("POST /logout", r, 200)

r = session.get(f"{BASE}/notes")
test("GET /notes (after logout)", r, 401)

# ── Summary ──────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"RESULTS: {passed} passed, {failed} failed, {passed + failed} total")
print("=" * 60)
sys.exit(0 if failed == 0 else 1)
