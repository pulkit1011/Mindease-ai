"""Wellness check-in: create, review, edit and delete entries."""
from datetime import date, datetime

import streamlit as st

import config
import database
import ui
from services import wellness_service as wellness

ui.setup_page("Wellness check-in", "📝")
ui.page_header("Wellness check-in", "A quick, private moment to notice how you are doing.")
DB = config.get_db_path()


def mood_label(m):
    return f"{config.MOOD_SCALE[m][0]} {config.MOOD_SCALE[m][1]}"


tab_new, tab_history = st.tabs(["New check-in", "History: edit or delete"])

with tab_new:
    with st.form("checkin_form"):
        c1, c2 = st.columns(2)
        day = c1.date_input("Date", value=date.today(), max_value=date.today())
        clock = c2.time_input("Time", value=datetime.now().time().replace(second=0, microsecond=0))
        mood = st.radio("How are you feeling overall?", list(config.MOOD_SCALE), index=2,
                        format_func=mood_label, horizontal=True)
        stress = st.slider("Stress level (1 = very calm, 10 = extremely stressed)", 1, 10, 5)
        energy = st.slider("Energy level (1 = very low, 10 = very high)", 1, 10, 5)
        include_sleep = st.checkbox("Include sleep in this entry", value=True)
        sleep = st.number_input("Hours of sleep last night", min_value=0.0, max_value=24.0, value=7.0, step=0.5)
        feelings = st.multiselect("Which feelings fit right now? (optional)", config.FEELINGS)
        notes = st.text_area("Personal notes (optional)", max_chars=wellness.MAX_NOTES_LENGTH,
                             help="Stored only in the local database on this computer.")
        submitted = st.form_submit_button("Save check-in")
    if submitted:
        try:
            raw = {"entry_time": datetime.combine(day, clock), "mood": mood, "stress": stress, "energy": energy,
                   "sleep_hours": sleep if include_sleep else None, "feelings": feelings, "notes": notes}
            wellness.save_entry(DB, raw)
            st.success("Check-in saved.")
            st.markdown("**A short reflection**")
            st.markdown(wellness.build_reflection(wellness.validate_entry(raw)))
        except wellness.ValidationError as exc:
            for message in exc.errors:
                st.error(message)
        except Exception:
            st.error("Sorry, the check-in could not be saved. Please try again.")

with tab_history:
    entries = list(reversed(database.list_entries(DB)))
    if not entries:
        ui.empty_state("Saved check-ins will appear here.", "Use the New check-in tab to add your first one.")
    else:
        by_id = {e["id"]: e for e in entries}
        chosen = st.selectbox("Choose an entry", list(by_id), format_func=lambda i: (
            f"{by_id[i]['entry_time'][:16]}  |  mood {config.MOOD_SCALE[by_id[i]['mood']][0]}  |  "
            f"stress {by_id[i]['stress']}" + ("  |  demo data" if by_id[i]["is_demo"] else "")))
        e = by_id[chosen]
        when = datetime.strptime(e["entry_time"], database.TIME_FORMAT)
        with st.form(f"edit_form_{chosen}"):
            c1, c2 = st.columns(2)
            day = c1.date_input("Date", value=when.date(), max_value=date.today(), key=f"d_{chosen}")
            clock = c2.time_input("Time", value=when.time(), key=f"t_{chosen}")
            mood = st.radio("Mood", list(config.MOOD_SCALE), index=e["mood"] - 1, format_func=mood_label,
                            horizontal=True, key=f"m_{chosen}")
            stress = st.slider("Stress level", 1, 10, e["stress"], key=f"s_{chosen}")
            energy = st.slider("Energy level", 1, 10, e["energy"], key=f"e_{chosen}")
            has_sleep = st.checkbox("Include sleep", value=e["sleep_hours"] is not None, key=f"hs_{chosen}")
            sleep = st.number_input("Hours of sleep", 0.0, 24.0, float(e["sleep_hours"] or 7.0), 0.5, key=f"sl_{chosen}")
            feelings = st.multiselect("Feelings", config.FEELINGS,
                                      default=[f for f in e["feelings"] if f in config.FEELINGS], key=f"f_{chosen}")
            notes = st.text_area("Notes", value=e["notes"], max_chars=wellness.MAX_NOTES_LENGTH, key=f"n_{chosen}")
            save = st.form_submit_button("Save changes")
        if save:
            try:
                wellness.edit_entry(DB, chosen, {"entry_time": datetime.combine(day, clock), "mood": mood,
                                                 "stress": stress, "energy": energy,
                                                 "sleep_hours": sleep if has_sleep else None,
                                                 "feelings": feelings, "notes": notes})
                st.success("Entry updated. Reload the page to see the new values in the list.")
            except wellness.ValidationError as exc:
                for message in exc.errors:
                    st.error(message)
        st.divider()
        confirm = st.checkbox("I understand that deleting this entry cannot be undone", key=f"c_{chosen}")
        if st.button("Delete this entry", disabled=not confirm, key=f"del_{chosen}"):
            database.delete_entry(DB, chosen)
            st.success("Entry deleted. Reload the page to refresh the list.")
