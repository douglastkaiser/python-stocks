from __future__ import annotations

# mypy: ignore-errors

from python_stocks.dashboard.app import build_app
from dash import dcc


_EXPECTED_GRAPH_IDS = {
    "price-chart",
    "strategy-chart",
    "cost-impact-chart",
    "time-in-market-chart",
    "diagnostics-chart",
    "price-chart-secondary",
    "strategy-chart-secondary",
    "cost-impact-chart-secondary",
    "comparison-matrix",
    "timeline-overlay",
}


def _collect_graph_ids(node):
    ids = set()

    if isinstance(node, dcc.Graph):
        if node.id:
            ids.add(str(node.id))

    children = getattr(node, "children", None)
    if isinstance(children, (list, tuple)):
        for child in children:
            ids.update(_collect_graph_ids(child))
    elif children is not None:
        ids.update(_collect_graph_ids(children))

    return ids


def test_dashboard_layout_contains_expected_graphs():
    app = build_app()
    graph_ids = _collect_graph_ids(app.layout)
    assert _EXPECTED_GRAPH_IDS.issubset(graph_ids)


def test_dashboard_callback_registered():
    app = build_app()
    assert (
        app.callback_map
    ), "Expected at least one callback registered for the dashboard"
    for callback in app.callback_map.values():
        assert callback.get(
            "inputs"
        ), "Callback should define inputs for interactive updates"
        has_outputs = bool(
            callback.get("outputs")
            or callback.get("outputs_list")
            or callback.get("output")
        )
        assert has_outputs, "Callback should define outputs for interactive updates"
