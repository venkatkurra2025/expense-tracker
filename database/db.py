import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

DATABASE_PATH = "expense_tracker.db"


def get_db():
    """Open connection to SQLite database with row_factory and foreign keys enabled."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables using CREATE TABLE IF NOT EXISTS."""
    conn = get_db()
    cursor = conn.cursor()

    # Create users table
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "name TEXT NOT NULL, "
        "email TEXT UNIQUE NOT NULL, "
        "password_hash TEXT NOT NULL, "
        "created_at TEXT NOT NULL)"
    )

    # Create expenses table
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS expenses ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "user_id INTEGER NOT NULL, "
        "amount REAL NOT NULL, "
        "category TEXT NOT NULL, "
        "date TEXT NOT NULL, "
        "description TEXT, "
        "created_at TEXT NOT NULL, "
        "FOREIGN KEY (user_id) REFERENCES users(id))"
    )

    conn.commit()
    conn.close()


def seed_db():
    """Insert sample data for development (idempotent)."""
    conn = get_db()
    cursor = conn.cursor()

    # Check if users table already has data
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    # Insert demo user
    demo_password = generate_password_hash("demo123")
    now = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
        ("Demo User", "demo@spendly.com", demo_password, now)
    )

    # Get the demo user's ID
    cursor.execute("SELECT id FROM users WHERE email = ?", ("demo@spendly.com",))
    user_id = cursor.fetchone()[0]

    # Insert 8 sample expenses across categories
    sample_expenses = [
        (50.00, "Food", "2026-04-01", "Lunch at cafe"),
        (25.50, "Transport", "2026-04-02", "Uber ride"),
        (120.00, "Bills", "2026-04-03", "Electric bill"),
        (45.00, "Health", "2026-04-05", "Pharmacy"),
        (30.00, "Entertainment", "2026-04-07", "Movie tickets"),
        (85.00, "Shopping", "2026-04-08", "New shirt"),
        (15.00, "Food", "2026-04-09", "Coffee and snacks"),
        (20.00, "Other", "2026-04-10", "Miscellaneous"),
    ]

    for amount, category, date, description in sample_expenses:
        cursor.execute(
            "INSERT INTO expenses (user_id, amount, category, date, description, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, amount, category, date, description, now)
        )

    conn.commit()
    conn.close()
