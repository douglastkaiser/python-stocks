from __future__ import annotations

# mypy: ignore-errors

from typing import Set

import dash.dcc as dcc

from python_stocks.dashboard.app import build_app
from python_stocks.dashboard.theme import get_theme


def _collect_graphs_with_labels(node, inherited_label: str | None = None) -> Set[str]:
    labels = set()
    active_label = inherited_label
    try:
        props = node.to_plotly_json().get("props", {})
        active_label = props.get("aria-label") or inherited_label
    except Exception:
        active_label = inherited_label

    if isinstance(node, dcc.Graph) and getattr(node, "id", None) and active_label:
        labels.add(str(node.id))

    children = getattr(node, "children", None)
    if isinstance(children, (list, tuple)):
        for child in children:
            labels.update(_collect_graphs_with_labels(child, active_label))
    elif children is not None:
        labels.update(_collect_graphs_with_labels(children, active_label))

    return labels


def _contrast_ratio(hex_a: str, hex_b: str) -> float:
    def _luminance(hex_color: str) -> float:
        hex_color = hex_color.lstrip("#")
        rgb = [int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4)]

        def _channel(c: float) -> float:
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

        r, g, b = (_channel(c) for c in rgb)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    lum_a, lum_b = _luminance(hex_a), _luminance(hex_b)
    lighter, darker = max(lum_a, lum_b), min(lum_a, lum_b)
    return (lighter + 0.05) / (darker + 0.05)


def test_all_graphs_define_aria_labels():
    app = build_app()
    labeled_graphs = _collect_graphs_with_labels(app.layout)
    expected_graphs = {
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
        "price-spotlight",
        "strategy-spotlight",
        "cost-spotlight",
        "matrix-spotlight",
        "timeline-spotlight",
    }

    assert expected_graphs.issubset(labeled_graphs)


def test_theme_contrast_meets_wcag():
    threshold = 4.5
    for mode in ("light", "dark"):
        theme = get_theme(mode)
        assert _contrast_ratio(theme["text"], theme["background"]) >= threshold
        assert _contrast_ratio(theme["text"], theme["panel"]) >= threshold
