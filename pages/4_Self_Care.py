"""Self-care activity library. All activities are optional and are not medical treatment."""
import time
from datetime import datetime

import pandas as pd
import streamlit as st

import config
import database
import ui
from services import wellness_service as wellness

ui.setup_page("Self-care", "🧘")
ui.page_header("Self-care activities", "Short, optional exercises. They are general wellness tools, not treatment.")
DB = config.get_db_path()
BY_KEY = {a["key"]: a for a in wellness.ACTIVITIES}


def intro(key):
    a = BY_KEY[key]
    st.markdown(f"**Purpose:** {a['purpose']}")
    st.markdown(f"**Estimated time:** about {a['duration']} minute(s)")
    st.markdown("**Steps**")
    for i, step in enumerate(a["steps"], 1):
        st.markdown(f"{i}. {step}")


def mark_done(key):
    if st.button("Mark as completed", key=f"done_{key}"):
        database.add_activity_completion(DB, key, BY_KEY[key]["duration"])
        st.success("Nice work. Completion recorded.")


def countdown(seconds, label, box):
    for remaining in range(seconds, 0, -1):
        box.markdown(f"### {label}: {remaining}")
        time.sleep(1)


titles = [a["title"] for a in wellness.ACTIVITIES]
tabs = st.tabs(titles)
tab_for = dict(zip(BY_KEY, tabs))

with tab_for["breathing"]:
    intro("breathing")
    rounds = st.slider("Number of breathing rounds (14 seconds each)", 2, 8, 4)
    box = st.empty()
    if st.button("Start breathing exercise"):
        for r in range(1, rounds + 1):
            for phase, secs in (("Breathe in slowly", 4), ("Hold gently", 4), ("Breathe out slowly", 6)):
                countdown(secs, f"Round {r} of {rounds}. {phase}", box)
        box.markdown("### Finished. Notice how your body feels.")
    mark_done("breathing")

with tab_for["grounding"]:
    intro("grounding")
    done = [st.checkbox(s, key=f"g_{i}") for i, s in enumerate(BY_KEY["grounding"]["steps"])]
    st.progress(sum(done) / len(done), text=f"{sum(done)} of {len(done)} steps ticked")
    mark_done("grounding")

with tab_for["journaling"]:
    intro("journaling")
    prompt = st.selectbox("Choose a prompt", wellness.JOURNAL_PROMPTS)
    text = st.text_area("Write here (this text is not saved by the app)", height=200, key="journal_text")
    if text.strip():
        st.download_button("Download my writing as a text file", f"{prompt}\n\n{text}", file_name="journal.txt")
    mark_done("journaling")

with tab_for["mindfulness"]:
    intro("mindfulness")
    box2 = st.empty()
    if st.button("Start 1-minute timer"):
        countdown(60, "Focus on your breath. Seconds left", box2)
        box2.markdown("### Time is up. Take one more slow breath.")
    mark_done("mindfulness")

with tab_for["study_break"]:
    intro("study_break")
    c1, c2, c3 = st.columns(3)
    study = c1.number_input("Study block (minutes)", 5, 180, 25, 5)
    brk = c2.number_input("Break (minutes)", 1, 60, 5)
    rnd = c3.number_input("Rounds", 1, 10, 3)
    try:
        st.table(pd.DataFrame(wellness.study_plan(int(study), int(brk), int(rnd), datetime.now())))
    except wellness.ValidationError as exc:
        st.error(exc.errors[0])
    mark_done("study_break")

with tab_for["routine"]:
    intro("routine")
    ticks = [st.checkbox(item, key=f"r_{i}") for i, item in enumerate(wellness.ROUTINE_ITEMS)]
    st.progress(sum(ticks) / len(ticks), text=f"{sum(ticks)} of {len(ticks)} habits ticked today")
    st.caption("There is no right score. Even one small habit is a good start.")
    mark_done("routine")

st.divider()
st.subheader("Your recent activity")
done_list = database.list_activity_completions(DB)
if not done_list:
    ui.empty_state("No completed activities yet.")
else:
    st.dataframe(pd.DataFrame([{"Activity": wellness.ACTIVITY_TITLES.get(d["activity_key"], d["activity_key"]),
                                "Completed at": d["completed_at"]} for d in reversed(done_list[-10:])]),
                 hide_index=True)
