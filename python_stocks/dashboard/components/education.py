"""Narrative helpers and guided tooltips for the dashboard."""

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
            html.Strong("Myth busting:"),
            html.P(
                "Consistently beating the market isn't about heroic trades. It comes from repeatable rules, risk controls, and minimizing drag.",
                style={"marginBottom": "4px"},
            ),
            html.Ul(
                [
                    html.Li(
                        "Slower drawdowns often recover faster when costs stay contained."
                    ),
                    html.Li(
                        "Staying invested through noisy stretches keeps compounding intact."
                    ),
                    html.Li("Execution discipline can matter as much as entry timing."),
                ],
                style={"margin": 0, "paddingLeft": "18px"},
            ),
        ],
    )


def guidance_tooltips() -> List[html.Div]:
    return [
        html.Div(
            "Hover charts for guidance on interpreting signals.",
            title="Tooltips explain volatility bands, slippage estimates, and rule-of-thumb interpretations.",
            style={"color": "#6b7280", "fontSize": "13px"},
        ),
        html.Div(
            "Use the controls below to rerun the comparison in real time.",
            title="Adjust the lookback window, cost assumptions, and ticker to see how the narrative changes.",
            style={"color": "#6b7280", "fontSize": "13px"},
        ),
    ]
