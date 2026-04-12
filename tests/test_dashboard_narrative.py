from __future__ import annotations

import pandas as pd

from python_stocks.dashboard.components.narrative import build_market_narrative


def test_build_market_narrative_contains_metric_first_language():
    index = pd.date_range("2025-01-01", periods=90, freq="B")
    close = pd.Series(100 + (pd.Series(range(90), index=index) * 0.2), index=index)
    volume = pd.Series(1_000_000, index=index)

    narrative = build_market_narrative(
        close,
        volume,
        cost_bps=25,
        label="Price replay",
    )

    assert narrative.what_changed.startswith("Price replay: Close")
    assert "MA spread" in narrative.what_changed
    assert narrative.why_it_matters.startswith("Vol")
    assert "25 bps" in narrative.why_it_matters
    assert narrative.what_to_watch_next.startswith("Watch:")


def test_build_market_narrative_handles_short_history():
    index = pd.date_range("2025-01-01", periods=3, freq="B")
    close = pd.Series([100.0, 101.0, 101.5], index=index)
    volume = pd.Series([1000, 1050, 1100], index=index)

    narrative = build_market_narrative(close, volume, cost_bps=10, label="Signal")

    assert "Insufficient history" in narrative.what_changed
