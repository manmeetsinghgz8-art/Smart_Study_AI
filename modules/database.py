
import sqlite3
from pathlib import Path
from datetime import datetime

# Find the main project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database location
DB_PATH = BASE_DIR / "database" / "study_planner.db"


def get_connection():
    """Create a connection to the SQLite database."""

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        str(DB_PATH),
        timeout=30
    )

    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database():
    """Create all required database tables."""

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Student profile
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roll_number TEXT NOT NULL UNIQUE,
                semester INTEGER NOT NULL,
                branch TEXT NOT NULL,
                available_hours REAL NOT NULL,
                preferred_time TEXT NOT NULL,
                target_percentage REAL NOT NULL,
                current_percentage REAL NOT NULL,
                attendance REAL NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Subjects
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject_name TEXT NOT NULL,
                subject_code TEXT,
                obtained_marks REAL DEFAULT 0,
                maximum_marks REAL DEFAULT 100,
                attendance REAL DEFAULT 0,
                difficulty TEXT DEFAULT 'Medium',
                exam_date TEXT,
                total_units INTEGER DEFAULT 0,
                completed_units INTEGER DEFAULT 0,
                pending_assignments INTEGER DEFAULT 0,
                preparation_hours REAL DEFAULT 0,
                confidence INTEGER DEFAULT 5,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(student_id) REFERENCES students(id)
                    ON DELETE CASCADE
            )
        """)

        # Study tasks
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject_id INTEGER,
                task_title TEXT NOT NULL,
                task_date TEXT NOT NULL,
                start_time TEXT,
                end_time TEXT,
                planned_hours REAL DEFAULT 0,
                completed_hours REAL DEFAULT 0,
                status TEXT DEFAULT 'Pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(student_id) REFERENCES students(id)
                    ON DELETE CASCADE,
                FOREIGN KEY(subject_id) REFERENCES subjects(id)
                    ON DELETE SET NULL
            )
        """)

        # Study sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject_id INTEGER,
                study_date TEXT NOT NULL,
                duration_hours REAL DEFAULT 0,
                notes TEXT,
                FOREIGN KEY(student_id) REFERENCES students(id)
                    ON DELETE CASCADE,
                FOREIGN KEY(subject_id) REFERENCES subjects(id)
                    ON DELETE SET NULL
            )
        """)

        # ML predictions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                predicted_score REAL NOT NULL,
                risk_level TEXT NOT NULL,
                prediction_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(student_id) REFERENCES students(id)
                    ON DELETE CASCADE
            )
        """)

        connection.commit()

    finally:
        connection.close()


def get_profile():
    """Retrieve the most recently updated student profile."""

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT * FROM students
            ORDER BY updated_at DESC, id DESC
            LIMIT 1
        """)

        result = cursor.fetchone()

        return dict(result) if result else None

    finally:
        connection.close()


def save_profile(profile):
    """Insert a new profile or update an existing profile."""

    connection = get_connection()

    try:
        cursor = connection.cursor()

        existing = cursor.execute("""
            SELECT id FROM students
            WHERE roll_number = ?
        """, (profile["roll_number"],)).fetchone()

        if existing:
            cursor.execute("""
                UPDATE students
                SET name = ?,
                    semester = ?,
                    branch = ?,
                    available_hours = ?,
                    preferred_time = ?,
                    target_percentage = ?,
                    current_percentage = ?,
                    attendance = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                profile["name"],
                profile["semester"],
                profile["branch"],
                profile["available_hours"],
                profile["preferred_time"],
                profile["target_percentage"],
                profile["current_percentage"],
                profile["attendance"],
                datetime.now().isoformat(timespec="seconds"),
                existing["id"]
            ))

            student_id = existing["id"]

        else:
            cursor.execute("""
                INSERT INTO students (
                    name, roll_number, semester, branch,
                    available_hours, preferred_time,
                    target_percentage, current_percentage,
                    attendance
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile["name"],
                profile["roll_number"],
                profile["semester"],
                profile["branch"],
                profile["available_hours"],
                profile["preferred_time"],
                profile["target_percentage"],
                profile["current_percentage"],
                profile["attendance"]
            ))

            student_id = cursor.lastrowid

        connection.commit()

        return student_id

    finally:
        connection.close()


def get_database_info():
    """Return the database file location and student count."""

    connection = get_connection()

    try:
        count = connection.execute(
            "SELECT COUNT(*) FROM students"
        ).fetchone()[0]

        return {
            "database_path": str(DB_PATH),
            "student_count": count
        }

    finally:
        connection.close()

# --------------------------------------------------
# SUBJECT MANAGEMENT FUNCTIONS
# --------------------------------------------------

def get_subjects(student_id):
    """Retrieve all subjects belonging to a student."""

    connection = get_connection()

    try:
        rows = connection.execute("""
            SELECT * FROM subjects
            WHERE student_id = ?
            ORDER BY subject_name
        """, (student_id,)).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


def add_subject(student_id, subject):
    """Add a new subject to the database."""

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO subjects (
                student_id,
                subject_name,
                subject_code,
                obtained_marks,
                maximum_marks,
                attendance,
                difficulty,
                exam_date,
                total_units,
                completed_units,
                pending_assignments,
                preparation_hours,
                confidence
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            student_id,
            subject["subject_name"],
            subject["subject_code"],
            subject["obtained_marks"],
            subject["maximum_marks"],
            subject["attendance"],
            subject["difficulty"],
            subject["exam_date"],
            subject["total_units"],
            subject["completed_units"],
            subject["pending_assignments"],
            subject["preparation_hours"],
            subject["confidence"]
        ))

        subject_id = cursor.lastrowid
        connection.commit()

        return subject_id

    finally:
        connection.close()


def update_subject(subject_id, student_id, subject):
    """Update an existing subject."""

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE subjects
            SET subject_name = ?,
                subject_code = ?,
                obtained_marks = ?,
                maximum_marks = ?,
                attendance = ?,
                difficulty = ?,
                exam_date = ?,
                total_units = ?,
                completed_units = ?,
                pending_assignments = ?,
                preparation_hours = ?,
                confidence = ?
            WHERE id = ? AND student_id = ?
        """, (
            subject["subject_name"],
            subject["subject_code"],
            subject["obtained_marks"],
            subject["maximum_marks"],
            subject["attendance"],
            subject["difficulty"],
            subject["exam_date"],
            subject["total_units"],
            subject["completed_units"],
            subject["pending_assignments"],
            subject["preparation_hours"],
            subject["confidence"],
            subject_id,
            student_id
        ))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


def delete_subject(subject_id, student_id):
    """Delete a subject belonging to a student."""

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM subjects
            WHERE id = ? AND student_id = ?
        """, (subject_id, student_id))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()



def save_prediction(student_id, predicted_score, risk_level):
    """
    Save a machine-learning prediction in SQLite.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO predictions (
                student_id,
                predicted_score,
                risk_level
            )
            VALUES (?, ?, ?)
        """, (
            student_id,
            predicted_score,
            risk_level
        ))

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()


def get_predictions(student_id):
    """
    Retrieve prediction history for a student.
    """

    connection = get_connection()

    try:
        rows = connection.execute("""
            SELECT *
            FROM predictions
            WHERE student_id = ?
            ORDER BY prediction_date DESC
        """, (student_id,)).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()

# --------------------------------------------------
# STUDY SESSION TRACKING
# --------------------------------------------------

def save_study_task(
    student_id,
    subject_id,
    task_title,
    task_date,
    start_time,
    end_time,
    planned_hours
):
    """Save a planned study session in SQLite."""

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO study_tasks (
                student_id,
                subject_id,
                task_title,
                task_date,
                start_time,
                end_time,
                planned_hours,
                completed_hours,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, 'Pending')
        """, (
            student_id,
            subject_id,
            task_title,
            task_date,
            start_time,
            end_time,
            planned_hours
        ))

        task_id = cursor.lastrowid
        connection.commit()

        return task_id

    finally:
        connection.close()


def get_study_tasks(student_id, task_date=None):
    """Retrieve saved study tasks for a student."""

    connection = get_connection()

    try:
        if task_date:
            rows = connection.execute("""
                SELECT
                    study_tasks.*,
                    subjects.subject_name
                FROM study_tasks
                LEFT JOIN subjects
                    ON study_tasks.subject_id = subjects.id
                WHERE study_tasks.student_id = ?
                  AND study_tasks.task_date = ?
                ORDER BY study_tasks.start_time
            """, (student_id, task_date)).fetchall()
        else:
            rows = connection.execute("""
                SELECT
                    study_tasks.*,
                    subjects.subject_name
                FROM study_tasks
                LEFT JOIN subjects
                    ON study_tasks.subject_id = subjects.id
                WHERE study_tasks.student_id = ?
                ORDER BY study_tasks.task_date DESC,
                         study_tasks.start_time
            """, (student_id,)).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()


def update_study_task_status(
    task_id,
    student_id,
    completed
):
    """Mark a saved study task as completed or pending."""

    connection = get_connection()

    try:
        status = "Completed" if completed else "Pending"

        row = connection.execute("""
            SELECT planned_hours
            FROM study_tasks
            WHERE id = ? AND student_id = ?
        """, (task_id, student_id)).fetchone()

        if row is None:
            return False

        completed_hours = (
            float(row["planned_hours"]) if completed else 0.0
        )

        connection.execute("""
            UPDATE study_tasks
            SET status = ?,
                completed_hours = ?
            WHERE id = ? AND student_id = ?
        """, (
            status,
            completed_hours,
            task_id,
            student_id
        ))

        connection.commit()

        return True

    finally:
        connection.close()
