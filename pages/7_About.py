"""About the project."""
import streamlit as st

import ui

ui.setup_page("About", "ℹ️")
ui.page_header("About MindEase AI", "An AI-powered mental wellness assistant for youth (academic project).")
st.markdown("""
**Problem.** Many young people feel stress and anxiety but have limited access to timely, approachable support.

**Idea.** A friendly web app for mood check-ins, reflection, simple self-care exercises and a clearly limited
AI chat, with a safety layer and pointers to professional help.

**SDG 3 link.** Supports United Nations Sustainable Development Goal 3, *Good Health and Well-being*
(mental health and well-being), as an early, low-cost self-awareness tool, not a treatment.

**Built with.** Python, Streamlit, SQLite, pandas, Plotly and an optional language-model API.

**What it is not.** Not a diagnostic tool, therapist, or emergency service. It has not been clinically
validated or tested with real users, and no claims are made about health outcomes.

**Implemented:** check-ins (create/edit/delete), mood charts, dashboard, six self-care activities,
AI chat with offline fallback, rule-based safety layer, CSV export, deletion controls.
**Not implemented (future work):** user accounts, encryption at rest, saved chat history, multi-language
support, clinician review, real-user evaluation.

See `concept_notes.md`, `lean_canvas.md` and `README.md` in the project folder for full documentation.
""")
st.caption("Student project. Add your name, institution and supervisor in the project report.")
