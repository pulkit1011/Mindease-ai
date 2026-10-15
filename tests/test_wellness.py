from datetime import datetime

import pytest

import database
from services import wellness_service as w

NOW = datetime(2026, 3, 1, 12, 0)
VALID = {"mood": 3, "stress": 5, "energy": 5, "sleep_hours": 7, "feelings": ["Calm"],
         "notes": " hi ", "entry_time": datetime(2026, 3, 1, 9, 0)}


def test_valid_entry_is_cleaned():
    out = w.validate_entry(VALID, NOW)
    assert out["notes"] == "hi" and out["mood"] == 3


@pytest.mark.parametrize("field,value", [("mood", 0), ("mood", 6), ("stress", 0), ("stress", 11),
                                         ("energy", 0), ("energy", 11), ("mood", 2.5), ("mood", "abc"),
                                         ("mood", None), ("mood", True)])
def test_out_of_range_or_bad_numbers_rejected(field, value):
    with pytest.raises(w.ValidationError):
        w.validate_entry({**VALID, field: value}, NOW)


@pytest.mark.parametrize("field,value", [("mood", 1), ("mood", 5), ("stress", 1), ("stress", 10),
                                         ("energy", 1), ("energy", 10), ("sleep_hours", 0), ("sleep_hours", 24)])
def test_boundary_values_accepted(field, value):
    assert w.validate_entry({**VALID, field: value}, NOW)[field] == value


@pytest.mark.parametrize("sleep", [-1, 24.5, "x"])
def test_bad_sleep_rejected(sleep):
    with pytest.raises(w.ValidationError):
        w.validate_entry({**VALID, "sleep_hours": sleep}, NOW)


def test_sleep_is_optional():
    assert w.validate_entry({**VALID, "sleep_hours": None}, NOW)["sleep_hours"] is None


def test_unknown_feeling_notes_length_and_future_time_rejected():
    for bad in ({"feelings": ["Nonsense"]}, {"notes": "a" * 2001},
                {"entry_time": datetime(2027, 1, 1)}, {"entry_time": "not a date"}):
        with pytest.raises(w.ValidationError):
            w.validate_entry({**VALID, **bad}, NOW)


def test_all_errors_reported_together():
    with pytest.raises(w.ValidationError) as e:
        w.validate_entry({**VALID, "mood": 9, "stress": 99}, NOW)
    assert len(e.value.errors) == 2


def test_save_edit_roundtrip(db):
    eid = w.save_entry(db, VALID, NOW)
    assert w.edit_entry(db, eid, {**VALID, "mood": 4}, NOW)
    assert database.get_entry(db, eid)["mood"] == 4


def test_invalid_entry_is_not_saved(db):
    with pytest.raises(w.ValidationError):
        w.save_entry(db, {**VALID, "mood": 0}, NOW)
    assert database.list_entries(db) == []


def test_reflection_is_supportive_and_makes_no_diagnosis():
    text = w.build_reflection({"mood": 1, "stress": 10, "energy": 2, "sleep_hours": 4})
    low = text.lower()
    assert "professional" in low and "not a diagnosis" in low
    for banned in ("you have depression", "you are depressed", "disorder"):
        assert banned not in low


def test_study_plan_and_limits():
    plan = w.study_plan(25, 5, 2, datetime(2026, 1, 1, 10, 0))
    assert [p["kind"] for p in plan] == ["Study", "Break", "Study"]
    with pytest.raises(w.ValidationError):
        w.study_plan(1, 5, 2)


def test_demo_data_is_valid_and_deterministic():
    a = w.generate_demo_entries(5, seed=1, today=NOW)
    assert a == w.generate_demo_entries(5, seed=1, today=NOW)
    for e in a:
        w.validate_entry(e, datetime(2026, 12, 1))


def test_public_demo_mode_flag_and_default_path(monkeypatch, tmp_path):
    import config
    monkeypatch.setenv("MINDEASE_PUBLIC_DEMO", "1")
    assert config.is_public_demo()
    monkeypatch.setenv("MINDEASE_PUBLIC_DEMO", "0")
    monkeypatch.setenv("MINDEASE_DB_PATH", str(tmp_path / "x.db"))
    assert not config.is_public_demo() and config.get_db_path() == tmp_path / "x.db"
