from __future__ import annotations

# mypy: ignore-errors

import pandas as pd
from dash import html

from python_stocks.dashboard.app import _build_chart_metadata, _CHART_IDS, build_app
from python_stocks.dashboard.components.layout import data_provenance_panel
from python_stocks.dashboard.components.market import MarketSample


def _collect_ids(node):
    ids = set()
    node_id = getattr(node, "id", None)
    if node_id:
        ids.add(str(node_id))

    children = getattr(node, "children", None)
    if isinstance(children, (list, tuple)):
        for child in children:
            ids.update(_collect_ids(child))
    elif children is not None:
        ids.update(_collect_ids(children))
    return ids


def _to_text(node) -> str:
    if isinstance(node, str):
        return node
    children = getattr(node, "children", None)
    if isinstance(children, (list, tuple)):
        return " ".join(_to_text(child) for child in children)
    if children is None:
        return ""
    return _to_text(children)


def test_all_charts_have_metadata_slots():
    app = build_app()
    component_ids = _collect_ids(app.layout)
    expected = {f"{chart_id}-metadata" for chart_id in _CHART_IDS}
    assert expected.issubset(component_ids)


def test_data_provenance_panel_renders_stale_warning_when_required():
    panel = data_provenance_panel(
        theme_key="light",
        data_source="Unit test source",
        market_date="2026-04-10",
        last_refresh="2026-04-10 22:15:00 UTC",
        ticker="SPY",
        scope_label="window 90d",
        is_stale=True,
    )

    text = _to_text(panel)
    assert "Data may be stale" in text
    assert "Unit test source" in text


def test_metadata_changes_with_ticker_and_scope_inputs():
    stale_refresh = pd.Timestamp.now(tz="UTC") - pd.Timedelta(hours=30)
    sample = MarketSample(
        tickers=["AAPL", "MSFT"],
        history=pd.DataFrame(),
        data_source="Provider cache",
        market_date=pd.Timestamp("2026-04-10"),
        last_refresh=stale_refresh,
    )

    base = _build_chart_metadata(
        theme_key="light",
        ticker="AAPL",
        window=90,
        cost_bps=25,
        horizon=120,
        hero_ticker="AAPL",
        hero_preset="balanced",
        sample=sample,
    )
    updated = _build_chart_metadata(
        theme_key="light",
        ticker="MSFT",
        window=140,
        cost_bps=40,
        horizon=252,
        hero_ticker="MSFT",
        hero_preset="patient",
        sample=sample,
    )

    assert _to_text(base["price-chart-metadata"]) != _to_text(
        updated["price-chart-metadata"]
    )
    assert "MSFT" in _to_text(updated["price-chart-metadata"])
    assert "window 140d" in _to_text(updated["price-chart-metadata"])
    assert "Data may be stale" in _to_text(updated["price-chart-metadata"])
    assert isinstance(updated["price-chart-metadata"], html.Div)
