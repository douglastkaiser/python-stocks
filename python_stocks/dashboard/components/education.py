"""Analytical guidance helpers for the dashboard."""

from __future__ import annotations

from typing import List

from dash import html


def metric_callouts() -> html.Div:
    return html.Div(
        className="metric-callout-block",
        role="region",
        **{"aria-label": "Comparison metrics callouts"},
        style={
            "background": "linear-gradient(135deg, rgba(16,185,129,0.08), rgba(59,130,246,0.08))",
            "border": "1px solid rgba(255,255,255,0.08)",
            "padding": "12px",
            "borderRadius": "10px",
            "marginTop": "8px",
        },
        children=[
            html.Strong("Metric callouts:"),
            html.P(
                "Participation ratio: 92% in-market in baseline replay.",
                style={"marginBottom": "2px"},
            ),
            html.P(
                "Cost envelope: modeled drag stays below 40 bps across presets.",
                style={"marginBottom": "2px"},
            ),
            html.P(
                "Regime checkpoints: compare 60d, 120d, and 252d overlays before reallocating.",
                style={"marginBottom": 0},
            ),
        ],
    )


def guidance_tooltips() -> List[html.Div]:
    return [
        html.Div(
            "Hover charts to inspect confidence and sensitivity cues.",
            title="Tooltips highlight volatility ranges, slippage sensitivity, and confidence under changing assumptions.",
            style={"color": "#6b7280", "fontSize": "13px"},
        ),
        html.Div(
            "Adjust controls to quantify tradeoff changes in real time.",
            title="Change lookback, cost drag, and ticker to measure return-volatility-cost tradeoffs before acting.",
            style={"color": "#6b7280", "fontSize": "13px"},
        ),
    ]
