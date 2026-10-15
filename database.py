"""SQLite data layer. Every function takes the database path so tests can use a
temporary database. All SQL uses parameter placeholders (?), never string formatting
of user data."""
import csv
import io
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

# ---- Schema migrations -------------------------------------------------------
# PRAGMA user_version stores the current schema version inside the database file.
# To change the schema later, add MIGRATIONS[2] = [...] and the app upgrades
# existing databases automatically on start-up.
MIGRATIONS = {
    1: [
        """CREATE TABLE IF NOT EXISTS wellness_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_time TEXT NOT NULL,
            mood INTEGER NOT NULL CHECK (mood BETWEEN 1 AND 5),
            stress INTEGER NOT NULL CHECK (stress BETWEEN 1 AND 10),
            energy INTEGER NOT NULL CHECK (energy BETWEEN 1 AND 10),
            sleep_hours REAL CHECK (sleep_hours IS NULL OR (sleep_hours >= 0 AND sleep_hours <= 24)),
            feelings TEXT NOT NULL DEFAULT '',
            notes TEXT NOT NULL DEFAULT '',
            is_demo INTEGER NOT NULL DEFAULT 0 CHECK (is_demo IN (0, 1)),
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        )""",
        "CREATE INDEX IF NOT EXISTS idx_entries_time ON wellness_entries(entry_time)",
        """CREATE TABLE IF NOT EXISTS activity_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_key TEXT NOT NULL,
            completed_at TEXT NOT NULL,
            duration_minutes INTEGER CHECK (duration_minutes IS NULL OR duration_minutes >= 0),
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )""",
    ],
}
LATEST_VERSION = max(MIGRATIONS)
FEELING_SEP = "|"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def connect(db_path) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_conn(db_path):
    """Open a connection, commit on success, roll back on error, always close."""
    conn = connect(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path) -> int:
    """Create or upgrade the database. Safe to call on every start-up."""
    with get_conn(db_path) as conn:
        current = conn.execute("PRAGMA user_version").fetchone()[0]
        for version in range(current + 1, LATEST_VERSION + 1):
            for statement in MIGRATIONS[version]:
                conn.execute(statement)
            conn.execute(f"PRAGMA user_version = {int(version)}")  # int-cast: not user data
    return LATEST_VERSION


def _row_to_entry(row) -> dict:
    d = dict(row)
    d["feelings"] = [f for f in d["feelings"].split(FEELING_SEP) if f]
    return d


def _fmt_time(value) -> str:
    return value.strftime(TIME_FORMAT) if isinstance(value, datetime) else str(value)


# ---- Wellness entries --------------------------------------------------------
def add_entry(db_path, entry: dict, is_demo: bool = False) -> int:
    with get_conn(db_path) as conn:
        cur = conn.execute(
            """INSERT INTO wellness_entries
               (entry_time, mood, stress, energy, sleep_hours, feelings, notes, is_demo)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (_fmt_time(entry["entry_time"]), entry["mood"], entry["stress"], entry["energy"],
             entry.get("sleep_hours"), FEELING_SEP.join(entry.get("feelings", [])),
             entry.get("notes", ""), 1 if is_demo else 0),
        )
        return cur.lastrowid


def get_entry(db_path, entry_id: int):
    with get_conn(db_path) as conn:
        row = conn.execute("SELECT * FROM wellness_entries WHERE id = ?", (entry_id,)).fetchone()
    return _row_to_entry(row) if row else None


def list_entries(db_path, start: str = None, end: str = None) -> list:
    """Entries ordered oldest to newest. start/end are 'YYYY-MM-DD' (inclusive)."""
    query, params, clauses = "SELECT * FROM wellness_entries", [], []
    if start:
        clauses.append("date(entry_time) >= ?")
        params.append(str(start))
    if end:
        clauses.append("date(entry_time) <= ?")
        params.append(str(end))
    if clauses:
        query += " WHERE " + " AND ".join(clauses)  # only fixed text is joined
    query += " ORDER BY entry_time ASC, id ASC"
    with get_conn(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
    return [_row_to_entry(r) for r in rows]


def update_entry(db_path, entry_id: int, entry: dict) -> bool:
    with get_conn(db_path) as conn:
        cur = conn.execute(
            """UPDATE wellness_entries
               SET entry_time=?, mood=?, stress=?, energy=?, sleep_hours=?, feelings=?, notes=?,
                   updated_at=datetime('now')
               WHERE id=?""",
            (_fmt_time(entry["entry_time"]), entry["mood"], entry["stress"], entry["energy"],
             entry.get("sleep_hours"), FEELING_SEP.join(entry.get("feelings", [])),
             entry.get("notes", ""), entry_id),
        )
        return cur.rowcount > 0


def delete_entry(db_path, entry_id: int) -> bool:
    with get_conn(db_path) as conn:
        return conn.execute("DELETE FROM wellness_entries WHERE id = ?", (entry_id,)).rowcount > 0


def delete_all_entries(db_path, demo_only: bool = False) -> int:
    with get_conn(db_path) as conn:
        if demo_only:
            return conn.execute("DELETE FROM wellness_entries WHERE is_demo = 1").rowcount
        return conn.execute("DELETE FROM wellness_entries").rowcount


# ---- Activity completions ----------------------------------------------------
def add_activity_completion(db_path, activity_key: str, duration_minutes=None, completed_at=None) -> int:
    when = _fmt_time(completed_at or datetime.now())
    with get_conn(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO activity_completions (activity_key, completed_at, duration_minutes) VALUES (?, ?, ?)",
            (activity_key, when, duration_minutes),
        )
        return cur.lastrowid


def list_activity_completions(db_path) -> list:
    with get_conn(db_path) as conn:
        rows = conn.execute("SELECT * FROM activity_completions ORDER BY completed_at ASC, id ASC").fetchall()
    return [dict(r) for r in rows]


def delete_all_activity_completions(db_path) -> int:
    with get_conn(db_path) as conn:
        return conn.execute("DELETE FROM activity_completions").rowcount


# ---- CSV export --------------------------------------------------------------
def _csv_safe(value):
    """Prevent spreadsheet formula injection: cells starting with = + - @ get a leading quote."""
    if isinstance(value, str) and value[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + value
    return value


def _to_csv(rows: list, columns: list) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(columns)
    for r in rows:
        writer.writerow([_csv_safe(r.get(c)) if r.get(c) is not None else "" for c in columns])
    return buffer.getvalue()


def export_entries_csv(db_path) -> str:
    rows = list_entries(db_path)
    for r in rows:
        r["feelings"] = ", ".join(r["feelings"])
    cols = ["id", "entry_time", "mood", "stress", "energy", "sleep_hours", "feelings", "notes",
            "is_demo", "created_at", "updated_at"]
    return _to_csv(rows, cols)


def export_activities_csv(db_path) -> str:
    return _to_csv(list_activity_completions(db_path),
                   ["id", "activity_key", "completed_at", "duration_minutes", "created_at"])
