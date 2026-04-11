"""Analytical guidance helpers for the dashboard."""

from __future__ import annotations

from typing import List

from dash import html


def myth_busting_callouts() -> html.Div:
    return html.Div(
        style={
            "background": "linear-gradient(135deg, rgba(16,185,129,0.08), rgba(59,130,246,0.08))",
            "border": "1px solid rgba(255,255,255,0.08)",
            "padding": "12px",
            "borderRadius": "10px",
            "marginTop": "8px",
        },
        children=[
            html.Strong("Context note:"),
            html.P(
                "Treat this as a confidence check: edge quality depends on stable rules, risk controls, and disciplined cost assumptions.",
                style={"marginBottom": "4px"},
            ),
            html.Ul(
                [
                    html.Li(
                        "Lower turnover can improve recovery odds when execution drag rises."
                    ),
                    html.Li(
                        "Participation stability often matters more than precise turning-point calls."
                    ),
                    html.Li("Revisit sensitivity bands before increasing risk or allocation."),
                ],
                style={"margin": 0, "paddingLeft": "18px"},
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
