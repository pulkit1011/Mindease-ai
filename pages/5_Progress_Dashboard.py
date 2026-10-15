"""Progress dashboard: summaries computed only from the user's own records."""
import streamlit as st

import charts
import config
import database
import ui
from services import analytics_service as analytics
from services import wellness_service as wellness

ui.setup_page("Progress dashboard", "📊")
ui.page_header("Progress dashboard", "A summary of your own check-ins and activities.")
DB = config.get_db_path()

df = analytics.entries_to_df(database.list_entries(DB))
activities = database.list_activity_completions(DB)
m = analytics.summary_metrics(df, activities)

if m["total_checkins"] == 0 and not activities:
    ui.empty_state("Your numbers will appear here after your first check-in.")
else:
    if df["is_demo"].fillna(0).astype(bool).any():
        st.warning("These numbers include FICTIONAL demo data. Remove it on the Mood tracker page.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total check-ins", m["total_checkins"])
    c2.metric("Active check-in days", m["active_days"])
    c3.metric("Activities completed", m["activities_completed"])
    c4, c5, c6 = st.columns(3)
    c4.metric("Average mood, last 7 days", "Not enough data" if m["recent_avg_mood"] is None
              else f"{m['recent_avg_mood']} / 5")

    def change_text(v):
        return "Not enough data" if v is None else f"{v:+.1f} points"
    c5.metric("Stress: last 7 days vs previous 7", change_text(m["stress_change"]))
    c6.metric("Energy: last 7 days vs previous 7", change_text(m["energy_change"]))

    daily = analytics.daily_averages(df)
    if not daily.empty:
        st.plotly_chart(charts.trend_chart(daily, "mood", "Average mood per day", "Mood (1-5)", [0.5, 5.5],
                                           "#5B50A0", "circle"))
    if activities:
        counts = {}
        for a in activities:
            title = wellness.ACTIVITY_TITLES.get(a["activity_key"], a["activity_key"])
            counts[title] = counts.get(title, 0) + 1
        st.markdown("**Completed activities**")
        st.table([{"Activity": k, "Times completed": v} for k, v in counts.items()])

with st.expander("What these numbers mean, and their limits", expanded=True):
    st.markdown(
        "- These figures are calculated only from what **you** entered on this device.\n"
        "- A mood score is a personal rating from 1 to 5. It is not a clinical measurement.\n"
        "- 'Change' compares your average in the last 7 days with the 7 days before. It needs entries in both windows.\n"
        "- A lower stress number or higher mood does **not** prove that you have improved clinically, and a "
        "worse week does not mean something is wrong with you. Many things affect daily scores.\n"
        "- This app does not label anyone as healthy or unhealthy and cannot diagnose any condition. "
        "If you are worried about how you feel, speak with a qualified professional.")
