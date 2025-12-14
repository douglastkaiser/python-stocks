from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pandas as pd

from python_stocks.dashboard.components.figures import (
    cost_impact_figure,
    diagnostics_figure,
    price_trend_figure,
    strategy_signal_figure,
    time_in_market_figure,
)
from python_stocks.dashboard.components.market import MarketSample
from python_stocks.dashboard.theme import get_theme


os.environ.setdefault("PYTHON_STOCKS_TEST_MODE", "1")

SNAPSHOT_DIR = Path(__file__).parent / "snapshots"


def _sample_history() -> MarketSample:
    dates = pd.date_range("2023-01-01", periods=8, freq="D")
    frame = pd.DataFrame(
        {
            ("AAA", "Close"): [100, 101, 102, 103, 104, 105, 104, 103],
            ("AAA", "Volume"): [1_000, 1_050, 980, 1_020, 990, 1_100, 1_200, 1_150],
            ("BBB", "Close"): [90, 92, 94, 93, 95, 96, 97, 98],
            ("BBB", "Volume"): [800, 820, 840, 830, 850, 860, 870, 880],
        },
        index=dates,
    )
    return MarketSample(tickers=["AAA", "BBB"], history=frame)


def _normalize(fig) -> dict:
    payload = json.loads(fig.to_json())
    payload.pop("frames", None)
    layout = payload.get("layout", {})
    layout.pop("uid", None)
    layout.pop("template", None)
    layout.pop("transition", None)
    for trace in payload.get("data", []):
        trace.pop("uid", None)
    return payload


def _assert_snapshot(fig, name: str) -> None:
    payload = _normalize(fig)
    snapshot_path = SNAPSHOT_DIR / f"{name}.json"
    assert snapshot_path.exists(), f"Missing snapshot for {name}"
    expected = json.loads(snapshot_path.read_text())
    payload_str = json.dumps(payload, sort_keys=True)
    expected_str = json.dumps(expected, sort_keys=True)
    if payload_str != expected_str:
        print(
            f"snapshot mismatch for {name}: payload={hashlib.sha256(payload_str.encode()).hexdigest()} expected={hashlib.sha256(expected_str.encode()).hexdigest()}"
        )
    assert payload_str == expected_str


def test_figures_match_snapshots():
    sample = _sample_history()
    theme = get_theme("light")

    snapshots = {
        "price_trend": price_trend_figure(sample, "AAA", theme),
        "strategy_signal": strategy_signal_figure(sample, "AAA", theme),
        "cost_impact": cost_impact_figure(sample, "AAA", theme),
        "time_in_market": time_in_market_figure(sample, "AAA", theme),
        "diagnostics": diagnostics_figure(sample, "AAA", theme),
    }

    for name, fig in snapshots.items():
        _assert_snapshot(fig, name)
