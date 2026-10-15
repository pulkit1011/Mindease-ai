import csv
import io
import sqlite3
from datetime import datetime

import pytest

import database

ENTRY = {"entry_time": datetime(2026, 1, 5, 9, 30), "mood": 3, "stress": 6, "energy": 5,
         "sleep_hours": 7.5, "feelings": ["Tired", "Calm"], "notes": "ok day"}


def test_init_creates_tables_and_is_repeatable(tmp_path):
    path = tmp_path / "a.db"
    assert database.init_db(path) == database.LATEST_VERSION
    assert database.init_db(path) == database.LATEST_VERSION
    with database.get_conn(path) as c:
        names = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"wellness_entries", "activity_completions"} <= names


def test_add_and_get_entry(db):
    eid = database.add_entry(db, ENTRY)
    got = database.get_entry(db, eid)
    assert got["mood"] == 3 and got["feelings"] == ["Tired", "Calm"] and got["is_demo"] == 0
    assert got["entry_time"] == "2026-01-05 09:30:00"


def test_get_missing_entry_returns_none(db):
    assert database.get_entry(db, 999) is None


def test_update_and_delete(db):
    eid = database.add_entry(db, ENTRY)
    assert database.update_entry(db, eid, {**ENTRY, "mood": 5, "notes": "better"})
    assert database.get_entry(db, eid)["mood"] == 5
    assert database.delete_entry(db, eid)
    assert database.get_entry(db, eid) is None
    assert not database.delete_entry(db, eid)
    assert not database.update_entry(db, eid, ENTRY)


def test_database_constraints_reject_bad_values(db):
    with pytest.raises(sqlite3.IntegrityError):
        database.add_entry(db, {**ENTRY, "mood": 9})
    with pytest.raises(sqlite3.IntegrityError):
        database.add_entry(db, {**ENTRY, "stress": 0})


def test_date_range_filter(db):
    database.add_entry(db, {**ENTRY, "entry_time": datetime(2026, 1, 1, 8)})
    database.add_entry(db, {**ENTRY, "entry_time": datetime(2026, 1, 10, 8)})
    assert len(database.list_entries(db)) == 2
    assert len(database.list_entries(db, start="2026-01-05")) == 1
    assert len(database.list_entries(db, start="2026-01-01", end="2026-01-01")) == 1


def test_sql_injection_text_is_stored_as_plain_text(db):
    evil = "x'); DROP TABLE wellness_entries;--"
    eid = database.add_entry(db, {**ENTRY, "notes": evil})
    assert database.get_entry(db, eid)["notes"] == evil
    assert len(database.list_entries(db)) == 1


def test_delete_all_and_demo_only(db):
    database.add_entry(db, ENTRY)
    database.add_entry(db, ENTRY, is_demo=True)
    assert database.delete_all_entries(db, demo_only=True) == 1
    assert len(database.list_entries(db)) == 1
    assert database.delete_all_entries(db) == 1


def test_activity_completions(db):
    database.add_activity_completion(db, "breathing", 2)
    assert database.list_activity_completions(db)[0]["activity_key"] == "breathing"
    assert database.delete_all_activity_completions(db) == 1


def test_csv_export_has_header_and_rows(db):
    database.add_entry(db, ENTRY)
    rows = list(csv.reader(io.StringIO(database.export_entries_csv(db))))
    assert rows[0][:4] == ["id", "entry_time", "mood", "stress"]
    assert rows[1][2] == "3" and rows[1][6] == "Tired, Calm"


def test_csv_export_empty_and_formula_safe(db):
    assert database.export_entries_csv(db).strip().startswith("id,entry_time")
    database.add_entry(db, {**ENTRY, "notes": "=HYPERLINK(\"http://x\")"})
    assert "'=HYPERLINK" in database.export_entries_csv(db)
