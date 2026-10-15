"""Central configuration: paths, constants and environment-variable settings.

Secrets (the API key) are read from environment variables only. They are never
written in source code.
"""
import os
from pathlib import Path

try:  # python-dotenv is optional; the app works without it.
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:  # pragma: no cover
    pass

BASE_DIR = Path(__file__).resolve().parent
RESOURCES_PATH = BASE_DIR / "data" / "support_resources.json"

APP_NAME = "MindEase AI"
TAGLINE = "A gentle space for everyday stress, study pressure and well-being check-ins."

# Mood scale used throughout the app (1 = very low, 5 = very good).
MOOD_SCALE = {
    1: ("😞", "Very low"),
    2: ("😕", "Low"),
    3: ("😐", "Okay"),
    4: ("🙂", "Good"),
    5: ("😄", "Very good"),
}

FEELINGS = [
    "Calm", "Happy", "Hopeful", "Grateful", "Motivated", "Relaxed",
    "Tired", "Stressed", "Anxious", "Overwhelmed", "Lonely", "Sad",
    "Irritable", "Restless", "Unmotivated", "Distracted",
]

PLACEHOLDER_KEYS = {"", "your_api_key_here", "changeme"}


def is_public_demo() -> bool:
    """True when MINDEASE_PUBLIC_DEMO=1 (use for a public link, e.g. Streamlit Community Cloud)."""
    return os.getenv("MINDEASE_PUBLIC_DEMO", "").strip() == "1"


def get_db_path() -> Path:
    """Location of the SQLite file (override with MINDEASE_DB_PATH).

    In public demo mode every browser session gets its OWN temporary database, so visitors
    never see each other's entries. These temporary files disappear when the server restarts."""
    if is_public_demo():
        try:
            import streamlit as st
            if "demo_db_path" not in st.session_state:
                import tempfile
                import uuid
                st.session_state["demo_db_path"] = str(Path(tempfile.gettempdir()) / f"mindease_{uuid.uuid4().hex}.db")
            return Path(st.session_state["demo_db_path"])
        except Exception:  # not running inside Streamlit
            pass
    return Path(os.getenv("MINDEASE_DB_PATH") or BASE_DIR / "data" / "mindease.db")


def _float_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def get_ai_settings() -> dict:
    """Read AI settings from the environment at call time (so tests can change them)."""
    return {
        "api_key": (os.getenv("ANTHROPIC_API_KEY") or "").strip(),
        "model": os.getenv("ANTHROPIC_MODEL") or "claude-sonnet-5-5",
        "timeout": _float_env("AI_TIMEOUT_SECONDS", 20.0),
        "max_tokens": int(_float_env("AI_MAX_TOKENS", 500)),
    }
