# MindEase AI: An AI-Powered Mental Wellness Assistant for Youth

A Streamlit web app for mood check-ins, reflection, self-care exercises and a safety-aware chat, built as a
B.Tech project aligned with **UN SDG 3 (Good Health and Well-being)**.

> **Important.** MindEase AI is a general wellness and educational tool. It is **not** a medical device, a
> diagnostic tool, a replacement for a therapist, or an emergency service. It is not monitored by any person.
> If you or someone else may be in danger, contact your local emergency services.

## What it does
- **Wellness check-in:** mood (1-5), stress (1-10), energy (1-10), optional sleep, feelings, notes; a short
  supportive reflection; edit and delete past entries.
- **AI chat:** supportive conversation about everyday stress. Works **without an API key** using clearly labelled offline replies.
- **Mood tracker:** Plotly charts for mood distribution, stress, energy and sleep with a date-range filter.
- **Self-care:** timed breathing, 5-4-3-2-1 grounding, journaling prompts, 1-minute mindfulness, study-break planner, routine checklist.
- **Progress dashboard:** metrics calculated only from your own records, with explanations of their limits.
- **Help and support:** limits, editable support-contact list, CSV export, deletion controls.
- **Safety module:** rule-based detection of high-risk messages that runs *before* any AI call and works offline.

## Limitations (read these)
- Safety detection is a simple pattern check. It is **not** clinically validated and can miss crises or flag harmless text.
- Support phone numbers in `data/support_resources.json` are **marked unverified**; they were written without live checking. Verify them before real use (see below).
- Data lives in a local SQLite file with **no login or encryption**. It is not a secure multi-user service.


## Tech stack
Python 3.11+ (developed on 3.12) · Streamlit · SQLite (`sqlite3`) · pandas · Plotly · Anthropic Python SDK (optional) · python-dotenv · pytest

## Folder structure
```
mindease-ai/
  app.py                    Home page (entry point)
  config.py                 settings, constants, environment variables
  database.py               SQLite schema, migrations, CRUD, CSV export
  ui.py                     shared theme/CSS and page helpers
  charts.py                 Plotly chart builders
  requirements.txt  .env.example  .gitignore
  .streamlit/config.toml    theme colours
  data/support_resources.json   editable support contacts (no code change needed)
  pages/                    1_Wellness_Checkin, 2_AI_Chat, 3_Mood_Tracker, 4_Self_Care,
                            5_Progress_Dashboard, 6_Help_and_Support, 7_About
  services/                 wellness_service, analytics_service, safety_service, ai_service
  tests/                    test_database, test_wellness, test_safety, test_analytics, test_ai_service, conftest
  concept_notes.md  lean_canvas.md  project_report.md  presentation_outline.md
  viva_questions.md  references.md
```




