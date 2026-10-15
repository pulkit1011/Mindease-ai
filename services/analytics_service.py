"""Pandas helpers that turn saved entries into chart data and summary numbers.
Every function handles an empty dataset without raising."""
from datetime import date, datetime, timedelta

import pandas as pd

from config import MOOD_SCALE

COLUMNS = ["id", "entry_time", "date", "mood", "stress", "energy", "sleep_hours", "feelings", "is_demo"]


def entries_to_df(entries: list) -> pd.DataFrame:
    if not entries:
        return pd.DataFrame(columns=COLUMNS)
    df = pd.DataFrame(entries)
    df["entry_time"] = pd.to_datetime(df["entry_time"])
    df["date"] = df["entry_time"].dt.date
    for col in ("mood", "stress", "energy", "sleep_hours"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df[COLUMNS].sort_values("entry_time").reset_index(drop=True)


def mood_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Count of entries per mood level (all five levels always present)."""
    counts = df["mood"].value_counts() if not df.empty else pd.Series(dtype=int)
    rows = [{"mood": m, "label": f"{emoji} {label}", "count": int(counts.get(m, 0))}
            for m, (emoji, label) in MOOD_SCALE.items()]
    return pd.DataFrame(rows)


def daily_averages(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["date", "mood", "stress", "energy", "sleep_hours"])
    out = df.groupby("date")[["mood", "stress", "energy", "sleep_hours"]].mean().reset_index()
    return out.round(2)


def _window_mean(df, column, start: date, end: date):
    sel = df[(df["date"] >= start) & (df["date"] <= end)][column].dropna()
    return float(sel.mean()) if len(sel) else None


def summary_metrics(df: pd.DataFrame, activities: list, today: date = None) -> dict:
    """Metrics from the user's real records. 'recent' = last 7 days including today,
    'previous' = the 7 days before that. Changes are None when either window is empty."""
    today = today or date.today()
    r_start, r_end = today - timedelta(days=6), today
    p_start, p_end = today - timedelta(days=13), today - timedelta(days=7)

    def change(col):
        if df.empty:
            return None
        recent, prev = _window_mean(df, col, r_start, r_end), _window_mean(df, col, p_start, p_end)
        return None if recent is None or prev is None else round(recent - prev, 2)

    recent_mood = None if df.empty else _window_mean(df, "mood", r_start, r_end)
    return {
        "total_checkins": int(len(df)),
        "active_days": int(df["date"].nunique()) if not df.empty else 0,
        "recent_avg_mood": None if recent_mood is None else round(recent_mood, 2),
        "stress_change": change("stress"),
        "energy_change": change("energy"),
        "activities_completed": len(activities),
    }
