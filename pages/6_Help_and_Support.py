"""Help, support resources and the user's data controls (export and delete)."""
import streamlit as st

import config
import database
import ui
from services import safety_service

ui.setup_page("Help and support", "🆘")
ui.page_header("Help and support", "What this app can and cannot do, who to contact, and your data.")
DB = config.get_db_path()

st.error("**If you or someone else may be in immediate danger, contact your local emergency services now.** "
         "This app cannot call anyone for you.")

st.subheader("Limits of this app")
st.markdown(
    "- MindEase AI is a general wellness and education tool. It is **not** a medical device, therapy or "
    "emergency service, and it cannot diagnose conditions or advise on medicines.\n"
    "- It is **not monitored** by a person. Nobody is told when you write something concerning.\n"
    "- Its automatic safety check is simple and can miss signs of a crisis or flag harmless text.\n"
    "- Please see a qualified professional if stress, low mood or worry is persistent, severe, or affects "
    "your studies, sleep, relationships or daily life.")

st.subheader("Support contacts")
data = safety_service.load_resources()
resources = data["resources"]
if not resources:
    st.warning("No support resources could be loaded from data/support_resources.json.")
else:
    st.warning("Contact details below have **not all been verified**. Items marked 'Not yet verified' were added "
               "without live checking. Please confirm each one on its official website before relying on it. "
               "You can update `data/support_resources.json` without changing any code.")
    for r in resources:
        verified = safety_service.is_verified(r)
        tag = ('<span class="me-tag me-tag-ok">Verified on ' + str(r["verified_on"]) + "</span>") if verified \
            else '<span class="me-tag">Not yet verified</span>'
        body = f"{tag}<br>"
        body += f"<b>Contact:</b> {r['contact']}<br>" if r.get("contact") else "<i>Add contact details in the JSON file.</i><br>"
        body += f"<b>Use:</b> {r.get('intended_use', '')}<br>"
        body += f"<b>Hours:</b> {r.get('hours') or 'To be confirmed'}<br>"
        if r.get("source_url"):
            body += f"<b>Source:</b> <a href='{r['source_url']}' target='_blank' rel='noopener'>{r['source_url']}</a>"
        ui.card(r["name"], body)

st.subheader("Your data")
st.markdown(
    f"Your records are stored in a **local SQLite file** at `{DB}` on the computer running this app. "
    "That is fine for a personal demo but is **not** a secure multi-user service: anyone with access to the "
    "computer or file can read it, and there is no login. Chat messages are not saved.")
t_export, t_delete = st.tabs(["Export (CSV)", "Delete data"])
with t_export:
    st.download_button("Download check-ins (CSV)", database.export_entries_csv(DB), "mindease_checkins.csv", "text/csv")
    st.download_button("Download completed activities (CSV)", database.export_activities_csv(DB),
                       "mindease_activities.csv", "text/csv")
    st.caption("Exports contain your personal notes. Store them somewhere private.")
with t_delete:
    st.markdown("Deletion removes rows from the local database file and cannot be undone. Copies you "
                "already exported, or backups of the file you made, are not affected.")
    confirm = st.text_input("Type DELETE to enable the buttons below")
    ok = confirm.strip() == "DELETE"
    c1, c2, c3 = st.columns(3)
    if c1.button("Delete all check-ins", disabled=not ok):
        st.success(f"Deleted {database.delete_all_entries(DB)} check-in(s).")
    if c2.button("Delete activity history", disabled=not ok):
        st.success(f"Deleted {database.delete_all_activity_completions(DB)} activity record(s).")
    if c3.button("Delete demo data only", disabled=not ok):
        st.success(f"Deleted {database.delete_all_entries(DB, demo_only=True)} demo entry(ies).")
