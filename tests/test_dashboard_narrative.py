from __future__ import annotations

import pandas as pd

from python_stocks.dashboard.app import build_app
from python_stocks.dashboard.components.narrative import build_market_narrative

_REQUIRED_LABELS = {
    "What changed:",
    "Why it matters:",
    "What to watch next:",
}
_NARRATIVE_IDS = {
    "price-spotlight-narrative",
    "strategy-spotlight-narrative",
    "cost-spotlight-narrative",
    "matrix-spotlight-narrative",
    "timeline-spotlight-narrative",
}


def _collect_nodes(node):
    nodes = [node]
    children = getattr(node, "children", None)
    if isinstance(children, (list, tuple)):
        for child in children:
            nodes.extend(_collect_nodes(child))
    elif children is not None:
        nodes.extend(_collect_nodes(children))
    return nodes


def _collect_text(node) -> str:
    children = getattr(node, "children", None)
    if isinstance(children, str):
        return children
    if isinstance(children, (list, tuple)):
        return "".join(_collect_text(child) for child in children)
    if children is None:
        return ""
    return _collect_text(children)


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


def test_dashboard_narrative_blocks_include_required_labels_and_content():
    app = build_app()
    id_to_node = {
        str(getattr(node, "id")): node
        for node in _collect_nodes(app.layout)
        if getattr(node, "id", None) in _NARRATIVE_IDS
    }
    assert _NARRATIVE_IDS.issubset(id_to_node.keys())

    for narrative_id, node in id_to_node.items():
        row_nodes = list(getattr(node, "children", []) or [])
        labels = {
            _collect_text(row.children[0]).strip()
            for row in row_nodes
            if getattr(row, "children", None)
        }
        assert labels == _REQUIRED_LABELS, f"missing labels for {narrative_id}"
        values = [
            _collect_text(row.children[1]).strip()
            for row in row_nodes
            if getattr(row, "children", None)
        ]
        assert all(values), f"expected non-empty narrative values for {narrative_id}"
