"""Mood tracker: charts and table for a chosen date range."""
from datetime import date, timedelta

import streamlit as st

import charts
import config
import database
import ui
from services import analytics_service as analytics
from services import wellness_service as wellness

ui.setup_page("Mood tracker", "📈")
ui.page_header("Mood tracker", "See how your own check-ins change over time.")
DB = config.get_db_path()

all_entries = database.list_entries(DB)
if not all_entries:
    ui.empty_state("There are no check-ins to chart yet.", "Add one on the Wellness check-in page.")
else:
    today = date.today()
    picked = st.date_input("Date range", value=(today - timedelta(days=29), today), max_value=today)
    if isinstance(picked, (tuple, list)) and len(picked) == 2:
        start, end = picked
    else:
        start, end = (picked[0] if isinstance(picked, (tuple, list)) else picked), today
    entries = database.list_entries(DB, start.isoformat(), end.isoformat())
    df = analytics.entries_to_df(entries)

    if any(e["is_demo"] for e in entries):
        st.warning("This view includes FICTIONAL demo data (shown with is_demo = 1). It is not real user data.")
    if df.empty:
        ui.empty_state("No check-ins fall inside this date range.", "Try a wider range.")
    else:
        daily = analytics.daily_averages(df)
        st.plotly_chart(charts.mood_distribution_chart(analytics.mood_distribution(df)))
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(charts.trend_chart(daily, "stress", "Stress over time", "Stress (1-10)", [0, 10.5],
                                               "#B5524A", "diamond"))
        with c2:
            st.plotly_chart(charts.trend_chart(daily, "energy", "Energy over time", "Energy (1-10)", [0, 10.5],
                                               "#2F7D5B", "square"))
        if daily["sleep_hours"].notna().any():
            st.plotly_chart(charts.trend_chart(daily.dropna(subset=["sleep_hours"]), "sleep_hours",
                                               "Sleep duration", "Hours", [0, 12], "#4A7FB5", "circle"))
        else:
            st.caption("No sleep data in this range. Sleep is optional in the check-in.")
        with st.expander("Show entries as a table"):
            table = df[["entry_time", "mood", "stress", "energy", "sleep_hours"]].copy()
            table["feelings"] = [", ".join(f) for f in df["feelings"]]
            st.dataframe(table, hide_index=True)
        st.caption("Charts show your own self-reported numbers only. They cannot show whether you are well or unwell.")

with st.expander("Fictional demo data (for demonstrations only)"):
    st.write("Adds 14 randomly generated, clearly fictional entries so you can preview the charts. "
             "They are flagged as demo data and can be removed at any time.")
    c1, c2 = st.columns(2)
    if c1.button("Load fictional demo data"):
        for entry in wellness.generate_demo_entries():
            database.add_entry(DB, wellness.validate_entry(entry), is_demo=True)
        st.success("Demo data loaded. Reload the page to see it.")
    if c2.button("Remove demo data"):
        st.success(f"Removed {database.delete_all_entries(DB, demo_only=True)} demo entries. Reload the page.")
