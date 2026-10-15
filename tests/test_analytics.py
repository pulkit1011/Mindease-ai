from datetime import date, datetime

from services import analytics_service as a

TODAY = date(2026, 3, 10)


def _e(day, mood=3, stress=5, energy=5, sleep=7.0):
    return {"id": day, "entry_time": datetime(2026, 3, day, 9), "mood": mood, "stress": stress,
            "energy": energy, "sleep_hours": sleep, "feelings": [], "is_demo": 0}


def test_empty_data_does_not_crash():
    df = a.entries_to_df([])
    assert df.empty
    assert a.daily_averages(df).empty
    assert list(a.mood_distribution(df)["count"]) == [0, 0, 0, 0, 0]
    m = a.summary_metrics(df, [], TODAY)
    assert m["total_checkins"] == 0 and m["recent_avg_mood"] is None and m["stress_change"] is None


def test_distribution_counts():
    df = a.entries_to_df([_e(1, 5), _e(2, 5), _e(3, 1)])
    d = a.mood_distribution(df)
    assert d.loc[d["mood"] == 5, "count"].item() == 2 and d["count"].sum() == 3


def test_daily_average_merges_same_day():
    df = a.entries_to_df([_e(1, stress=4), {**_e(1), "id": 99, "stress": 8}])
    assert a.daily_averages(df)["stress"].item() == 6.0


def test_summary_counts_and_changes():
    entries = [_e(1, stress=8), _e(2, stress=8), _e(8, stress=4, mood=4), _e(9, stress=4, mood=5), _e(9, stress=4)]
    m = a.summary_metrics(a.entries_to_df(entries), [{"id": 1}], TODAY)
    assert m["total_checkins"] == 5 and m["active_days"] == 4 and m["activities_completed"] == 1
    assert m["stress_change"] == -4.0 and m["recent_avg_mood"] == 4.0


def test_change_is_none_without_previous_window():
    m = a.summary_metrics(a.entries_to_df([_e(9)]), [], TODAY)
    assert m["stress_change"] is None and m["recent_avg_mood"] == 3.0


def test_missing_sleep_values_are_handled():
    df = a.entries_to_df([_e(1, sleep=None)])
    assert a.daily_averages(df).shape[0] == 1
