"""MindEase AI home page. Run with:  streamlit run app.py"""
import streamlit as st

import config
import database
import ui

ui.setup_page("Home", "🌿")

st.markdown(f"""
<div class="me-hero">
  <h1>Welcome to {config.APP_NAME} 🌿</h1>
  <p style="font-size:1.1rem;margin:0">{config.TAGLINE}</p>
</div>
""", unsafe_allow_html=True)
ui.note(ui.SHORT_DISCLAIMER)

st.subheader("What would you like to do?")
FEATURES = [
    ("📝 Wellness check-in", "Record your mood, stress, energy and sleep in under a minute.", "pages/1_Wellness_Checkin.py"),
    ("💬 AI chat", "Talk through everyday stress, study pressure or motivation.", "pages/2_AI_Chat.py"),
    ("📈 Mood tracker", "See how your mood, stress and energy change over time.", "pages/3_Mood_Tracker.py"),
    ("🧘 Self-care", "Guided breathing, grounding, journaling and study breaks.", "pages/4_Self_Care.py"),
    ("📊 Progress dashboard", "A summary of your own check-ins and activities.", "pages/5_Progress_Dashboard.py"),
    ("🆘 Help and support", "Limits of this app, support contacts and your data controls.", "pages/6_Help_and_Support.py"),
]
for row_start in range(0, len(FEATURES), 3):
    cols = st.columns(3)
    for col, (title, text, page) in zip(cols, FEATURES[row_start:row_start + 3]):
        with col:
            ui.card(title, text)
            st.page_link(page, label="Open", icon="➡️")

st.subheader("Your snapshot")
entries = database.list_entries(config.get_db_path())
if entries:
    c1, c2 = st.columns(2)
    c1.metric("Check-ins saved on this device", len(entries))
    c2.metric("Most recent check-in", entries[-1]["entry_time"][:16])
    if any(e["is_demo"] for e in entries):
        st.warning("Some saved entries are fictional demo data. You can remove them on the Mood tracker page.")
else:
    ui.empty_state("You have not saved a check-in yet.", "Start with the Wellness check-in. It only takes a minute.")
st.caption("Your records are stored in a local file on the computer running this app. "
           "See Help and Support for details and deletion controls.")
