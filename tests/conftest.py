"""Shared pytest setup: make project modules importable and provide a temp database."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import database  # noqa: E402


@pytest.fixture
def db(tmp_path):
    """A fresh temporary database. The user's real database is never touched."""
    path = tmp_path / "test.db"
    database.init_db(path)
    return path
