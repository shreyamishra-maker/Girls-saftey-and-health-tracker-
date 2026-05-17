"""
database.py - SQLite database management for Girls Safety & Health Assistant
Handles all data storage: users, contacts, health logs, cycle data, notes
"""

import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = "safety_app.db"


def get_connection():
    """Return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def initialize_database():
    """Create all tables if they don't already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # ── Users ──────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            age         INTEGER,
            email       TEXT    UNIQUE NOT NULL,
            password    TEXT    NOT NULL,
            blood_group TEXT,
            created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Emergency Contacts ─────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emergency_contacts (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            name       TEXT    NOT NULL,
            phone      TEXT    NOT NULL,
            relation   TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── Menstrual Cycle Logs ───────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cycle_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            start_date  TEXT    NOT NULL,
            end_date    TEXT,
            cycle_length INTEGER DEFAULT 28,
            notes       TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── Symptom / Mood Logs ────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS symptom_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            log_date    TEXT    NOT NULL,
            headache    INTEGER DEFAULT 0,
            cramps      INTEGER DEFAULT 0,
            mood        TEXT,
            fatigue     INTEGER DEFAULT 0,
            bloating    INTEGER DEFAULT 0,
            notes       TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── Medical History Notes ──────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medical_notes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            title      TEXT    NOT NULL,
            content    TEXT,
            created_at TEXT    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── SOS Alert Log ─────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sos_logs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            latitude   REAL,
            longitude  REAL,
            address    TEXT,
            sent_at    TEXT    DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ── Reminders ─────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            reminder_type TEXT   NOT NULL,
            message      TEXT    NOT NULL,
            remind_date  TEXT    NOT NULL,
            is_done      INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] Database initialized successfully.")


# ══════════════════════════════════════════════════════════
#  USER OPERATIONS
# ══════════════════════════════════════════════════════════

def register_user(name, age, email, password, blood_group=""):
    """Register a new user. Returns (True, user_id) or (False, error_msg)."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, age, email, password, blood_group) VALUES (?,?,?,?,?)",
            (name, age, email, hash_password(password), blood_group)
        )
        conn.commit()
        return True, cursor.lastrowid
    except sqlite3.IntegrityError:
        return False, "Email already registered."
    finally:
        conn.close()


def login_user(email, password):
    """Validate login. Returns user row dict or None."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, hash_password(password))
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user(user_id):
    """Fetch a user by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_user(user_id, name, age, blood_group):
    """Update user profile details."""
    conn = get_connection()
    conn.execute(
        "UPDATE users SET name=?, age=?, blood_group=? WHERE id=?",
        (name, age, blood_group, user_id)
    )
    conn.commit()
    conn.close()


# ══════════════════════════════════════════════════════════
#  EMERGENCY CONTACTS
# ══════════════════════════════════════════════════════════

def add_contact(user_id, name, phone, relation=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO emergency_contacts (user_id, name, phone, relation) VALUES (?,?,?,?)",
        (user_id, name, phone, relation)
    )
    conn.commit()
    conn.close()


def get_contacts(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM emergency_contacts WHERE user_id=?", (user_id,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def delete_contact(contact_id):
    conn = get_connection()
    conn.execute("DELETE FROM emergency_contacts WHERE id=?", (contact_id,))
    conn.commit()
    conn.close()


# ══════════════════════════════════════════════════════════
#  CYCLE TRACKING
# ══════════════════════════════════════════════════════════

def add_cycle(user_id, start_date, end_date=None, cycle_length=28, notes=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO cycle_logs (user_id, start_date, end_date, cycle_length, notes) VALUES (?,?,?,?,?)",
        (user_id, start_date, end_date, cycle_length, notes)
    )
    conn.commit()
    conn.close()


def get_cycles(user_id, limit=6):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM cycle_logs WHERE user_id=? ORDER BY start_date DESC LIMIT ?",
        (user_id, limit)
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def predict_next_cycle(user_id):
    """
    Predict next period start date based on average cycle length
    from the last 3 logged cycles.
    """
    from datetime import timedelta
    cycles = get_cycles(user_id, limit=3)
    if not cycles:
        return None, "No cycle data available."

    avg_length = sum(c["cycle_length"] for c in cycles) / len(cycles)
    last_start = datetime.strptime(cycles[0]["start_date"], "%Y-%m-%d")
    next_start = last_start + timedelta(days=int(avg_length))
    return next_start.strftime("%Y-%m-%d"), f"Avg cycle: {int(avg_length)} days"


# ══════════════════════════════════════════════════════════
#  SYMPTOM LOGS
# ══════════════════════════════════════════════════════════

def add_symptom_log(user_id, log_date, headache=0, cramps=0, mood="", fatigue=0, bloating=0, notes=""):
    conn = get_connection()
    conn.execute(
        """INSERT INTO symptom_logs
           (user_id, log_date, headache, cramps, mood, fatigue, bloating, notes)
           VALUES (?,?,?,?,?,?,?,?)""",
        (user_id, log_date, headache, cramps, mood, fatigue, bloating, notes)
    )
    conn.commit()
    conn.close()


def get_symptom_logs(user_id, limit=10):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM symptom_logs WHERE user_id=? ORDER BY log_date DESC LIMIT ?",
        (user_id, limit)
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


# ══════════════════════════════════════════════════════════
#  MEDICAL NOTES
# ══════════════════════════════════════════════════════════

def add_medical_note(user_id, title, content):
    conn = get_connection()
    conn.execute(
        "INSERT INTO medical_notes (user_id, title, content) VALUES (?,?,?)",
        (user_id, title, content)
    )
    conn.commit()
    conn.close()


def get_medical_notes(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM medical_notes WHERE user_id=? ORDER BY created_at DESC",
        (user_id,)
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def delete_medical_note(note_id):
    conn = get_connection()
    conn.execute("DELETE FROM medical_notes WHERE id=?", (note_id,))
    conn.commit()
    conn.close()


# ══════════════════════════════════════════════════════════
#  SOS LOG
# ══════════════════════════════════════════════════════════

def log_sos(user_id, latitude, longitude, address=""):
    conn = get_connection()
    conn.execute(
        "INSERT INTO sos_logs (user_id, latitude, longitude, address) VALUES (?,?,?,?)",
        (user_id, latitude, longitude, address)
    )
    conn.commit()
    conn.close()


# ══════════════════════════════════════════════════════════
#  REMINDERS
# ══════════════════════════════════════════════════════════

def add_reminder(user_id, reminder_type, message, remind_date):
    conn = get_connection()
    conn.execute(
        "INSERT INTO reminders (user_id, reminder_type, message, remind_date) VALUES (?,?,?,?)",
        (user_id, reminder_type, message, remind_date)
    )
    conn.commit()
    conn.close()


def get_reminders(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM reminders WHERE user_id=? AND is_done=0 ORDER BY remind_date ASC",
        (user_id,)
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def mark_reminder_done(reminder_id):
    conn = get_connection()
    conn.execute("UPDATE reminders SET is_done=1 WHERE id=?", (reminder_id,))
    conn.commit()
    conn.close()
