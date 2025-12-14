"""Shared helpers for dashboard components."""

from __future__ import annotations

import plotly.graph_objects as go

from python_stocks.dashboard.theme import Theme
from python_stocks.plotting import TEST_MODE_FLAG


def apply_layout(fig: go.Figure, theme: Theme) -> go.Figure:
    """Apply consistent layout styling to figures."""
    fig.update_layout(
        template="plotly_dark" if theme["mode"] == "dark" else "plotly_white",
        plot_bgcolor=theme["plot_bg"],
        paper_bgcolor=theme["paper_bg"],
        font={"color": theme["text"]},
        margin={"l": 40, "r": 12, "t": 40, "b": 40},
        hovermode="x unified",
    )
    if TEST_MODE_FLAG:
        fig.update_layout(transition_duration=0)
    return fig
