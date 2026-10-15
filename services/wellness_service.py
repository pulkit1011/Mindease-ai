"""Validation, supportive reflections, activity definitions and demo data.

Nothing here diagnoses a condition. Reflections only restate what the user entered
and offer general self-care ideas."""
import random
from datetime import datetime, timedelta

import database
from config import FEELINGS

MAX_NOTES_LENGTH = 2000


class ValidationError(ValueError):
    """Raised with a list of readable messages when an entry is invalid."""

    def __init__(self, errors):
        self.errors = list(errors)
        super().__init__("; ".join(self.errors))


def _as_int(value, name, low, high, errors):
    if isinstance(value, bool) or value is None:
        errors.append(f"{name} is required and must be a whole number from {low} to {high}.")
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        errors.append(f"{name} must be a whole number from {low} to {high}.")
        return None
    if number != int(number) or not (low <= number <= high):
        errors.append(f"{name} must be a whole number from {low} to {high}.")
        return None
    return int(number)


def _parse_time(value, errors, now):
    if value is None:
        return now
    if isinstance(value, str):
        for fmt in (database.TIME_FORMAT, "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S"):
            try:
                value = datetime.strptime(value, fmt)
                break
            except ValueError:
                continue
        else:
            errors.append("Date and time could not be understood.")
            return None
    if not isinstance(value, datetime):
        errors.append("Date and time could not be understood.")
        return None
    if value > now + timedelta(minutes=5):
        errors.append("Date and time cannot be in the future.")
        return None
    return value.replace(microsecond=0)


def validate_entry(raw: dict, now: datetime = None) -> dict:
    """Return a clean entry dict or raise ValidationError listing every problem."""
    now = now or datetime.now()
    errors = []
    mood = _as_int(raw.get("mood"), "Mood", 1, 5, errors)
    stress = _as_int(raw.get("stress"), "Stress level", 1, 10, errors)
    energy = _as_int(raw.get("energy"), "Energy level", 1, 10, errors)

    sleep = raw.get("sleep_hours")
    if sleep is not None:
        try:
            sleep = float(sleep)
            if isinstance(raw.get("sleep_hours"), bool) or not (0 <= sleep <= 24):
                raise ValueError
        except (TypeError, ValueError):
            errors.append("Sleep duration must be a number of hours between 0 and 24.")
            sleep = None

    feelings = raw.get("feelings") or []
    if not isinstance(feelings, (list, tuple)) or any(f not in FEELINGS for f in feelings):
        errors.append("One or more selected feelings are not in the list.")
        feelings = []

    notes = raw.get("notes") or ""
    if not isinstance(notes, str):
        errors.append("Notes must be text.")
        notes = ""
    notes = notes.strip()
    if len(notes) > MAX_NOTES_LENGTH:
        errors.append(f"Notes are too long (maximum {MAX_NOTES_LENGTH} characters).")

    entry_time = _parse_time(raw.get("entry_time"), errors, now)
    if errors:
        raise ValidationError(errors)
    return {"entry_time": entry_time, "mood": mood, "stress": stress, "energy": energy,
            "sleep_hours": sleep, "feelings": list(dict.fromkeys(feelings)), "notes": notes}


def save_entry(db_path, raw: dict, now: datetime = None) -> int:
    return database.add_entry(db_path, validate_entry(raw, now))


def edit_entry(db_path, entry_id: int, raw: dict, now: datetime = None) -> bool:
    return database.update_entry(db_path, entry_id, validate_entry(raw, now))


def build_reflection(entry: dict) -> str:
    """A short, supportive message based only on the user's own answers."""
    mood, stress, energy = entry["mood"], entry["stress"], entry["energy"]
    sleep = entry.get("sleep_hours")
    parts = ["Thank you for checking in with yourself."]
    if stress >= 8:
        parts.append("You rated your stress as high today. A few slow breaths or a short walk "
                     "might take the edge off, and the Self-care page has a guided breathing exercise.")
    elif stress <= 3:
        parts.append("Your stress feels fairly low right now. It may help to notice what is supporting that.")
    else:
        parts.append("Your stress is somewhere in the middle. Small breaks between tasks can help.")
    if energy <= 3 or (sleep is not None and sleep < 6):
        parts.append("Your energy or sleep looks low. If you can, a gentle routine and some rest may help.")
    if mood <= 2:
        parts.append("It sounds like today feels heavy. Being kind to yourself matters, and talking with "
                     "a friend, family member or campus counsellor can help.")
    elif mood >= 4:
        parts.append("It is good to see a brighter mood today. Consider noting what helped.")
    if mood <= 2 or stress >= 9:
        parts.append("If feeling this way keeps happening or gets in the way of daily life, please consider "
                     "speaking with a qualified professional. See the Help and Support page.")
    parts.append("_This reflection uses only what you entered. It is general wellness information, "
                 "not a diagnosis or medical advice._")
    return " ".join(parts)


ACTIVITIES = [
    {"key": "breathing", "title": "Guided breathing", "duration": 2,
     "purpose": "Slow breathing can help you feel a little calmer when you are tense.",
     "steps": ["Sit comfortably and relax your shoulders.",
               "Breathe in slowly through your nose for 4 seconds.",
               "Hold gently for 4 seconds.",
               "Breathe out slowly for 6 seconds.",
               "Repeat for the number of rounds you choose."]},
    {"key": "grounding", "title": "5-4-3-2-1 grounding", "duration": 5,
     "purpose": "Bringing attention to your senses can help when thoughts are racing.",
     "steps": ["Name 5 things you can see.", "Notice 4 things you can feel (touch).",
               "Listen for 3 things you can hear.", "Notice 2 things you can smell.",
               "Notice 1 thing you can taste, then take one slow breath."]},
    {"key": "journaling", "title": "Journaling prompt", "duration": 10,
     "purpose": "Writing thoughts down can make them easier to understand.",
     "steps": ["Pick a prompt below, or write freely.",
               "Write for 5 to 10 minutes without worrying about grammar.",
               "Read it back kindly. Your text is not saved by this app."]},
    {"key": "mindfulness", "title": "One-minute mindfulness", "duration": 1,
     "purpose": "A short pause to notice the present moment without judging it.",
     "steps": ["Sit or stand comfortably.", "Focus on the feeling of your breath.",
               "When your mind wanders, gently return to the breath.",
               "At the end, notice how your body feels."]},
    {"key": "study_break", "title": "Study-break planner", "duration": 5,
     "purpose": "Plan focused study blocks with real breaks so you do not burn out.",
     "steps": ["Choose a study block and a break length.", "Choose how many rounds.",
               "Use breaks to stretch, drink water or look away from the screen."]},
    {"key": "routine", "title": "Healthy-routine checklist", "duration": 3,
     "purpose": "A simple reminder of everyday habits that support well-being.",
     "steps": ["Tick the habits you have done today.", "Pick one small habit to try tomorrow."]},
]
ACTIVITY_TITLES = {a["key"]: a["title"] for a in ACTIVITIES}

JOURNAL_PROMPTS = [
    "What is one thing weighing on my mind right now, and what is within my control?",
    "What is one small thing that went okay today?",
    "What would I say to a friend who felt the way I feel?",
    "What do I need more of, and less of, this week?",
]

ROUTINE_ITEMS = ["Drank enough water", "Ate a proper meal", "Moved my body for a few minutes",
                 "Spent time outside or near daylight", "Took a break from screens",
                 "Talked with someone I trust", "Planned a realistic bedtime"]


def study_plan(study_minutes: int, break_minutes: int, rounds: int, start: datetime = None) -> list:
    """Return a list of {'start','end','kind'} blocks for the study-break planner."""
    if not (5 <= study_minutes <= 180 and 1 <= break_minutes <= 60 and 1 <= rounds <= 10):
        raise ValidationError(["Study 5-180 min, break 1-60 min and 1-10 rounds are supported."])
    t = (start or datetime.now()).replace(second=0, microsecond=0)
    plan = []
    for i in range(rounds):
        for kind, length in (("Study", study_minutes), ("Break", break_minutes)):
            if kind == "Break" and i == rounds - 1:
                break
            end = t + timedelta(minutes=length)
            plan.append({"start": t.strftime("%H:%M"), "end": end.strftime("%H:%M"), "kind": kind})
            t = end
    return plan


def generate_demo_entries(days: int = 14, seed: int = 7, today: datetime = None) -> list:
    """FICTIONAL demonstration entries (random, seeded). Saved with is_demo=1."""
    rng = random.Random(seed)
    today = (today or datetime.now()).replace(hour=20, minute=0, second=0, microsecond=0)
    out = []
    for i in range(days, 0, -1):
        out.append({"entry_time": today - timedelta(days=i), "mood": rng.randint(2, 5),
                    "stress": rng.randint(3, 9), "energy": rng.randint(3, 8),
                    "sleep_hours": round(rng.uniform(5, 8.5), 1),
                    "feelings": rng.sample(FEELINGS, 2), "notes": "Fictional demo entry."})
    return out
