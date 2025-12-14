"""Comparison utilities for evaluating risk/return trade-offs."""

from __future__ import annotations

from typing import Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from python_stocks.dashboard.components.common import apply_layout
from python_stocks.dashboard.components.market import MarketSample
from python_stocks.dashboard.theme import Theme


def _risk_return(
    snapshot: pd.Series, window: int, cost_penalty: float
) -> Tuple[float, float, float]:
    returns = snapshot.pct_change().dropna()
    if returns.empty:
        return 0.0, 0.0, 0.0
    mean_return = returns.tail(window).mean() * 252
    vol = returns.tail(window).std() * np.sqrt(252)
    estimated_cost = cost_penalty * vol
    return mean_return, vol, estimated_cost


def comparison_matrix_figure(
    sample: MarketSample,
    ticker: str,
    theme: Theme,
    window: int = 60,
    cost_penalty: float = 0.002,
) -> go.Figure:
    """Plot return vs volatility and overlay execution cost."""
    points = []
    for symbol in sample.tickers:
        close_series = sample.history[symbol]["Close"].sort_index()
        mean_return, vol, est_cost = _risk_return(close_series, window, cost_penalty)
        points.append(
            {
                "symbol": symbol,
                "return": mean_return * 100,
                "vol": vol * 100,
                "cost": est_cost * 100,
            }
        )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[p["vol"] for p in points],
            y=[p["return"] for p in points],
            mode="markers+text",
            text=[p["symbol"] for p in points],
            textposition="top center",
            marker={
                "size": [max(12, p["cost"] * 80) for p in points],
                "color": [
                    theme["accent"] if p["symbol"] == ticker else theme["accent_alt"]
                    for p in points
                ],
                "line": {"width": 1, "color": theme["grid"]},
            },
            customdata=[p["cost"] for p in points],
            hovertemplate="<b>%{text}</b><br>Volatility: %{x:.2f}%<br>Return: %{y:.2f}%<br>Impact cost: %{customdata:.2f}%",
            showlegend=False,
        )
    )

    fig.add_annotation(
        text="Bigger bubbles = more slippage drag. High return with lower volatility signals efficient compounding.",
        xref="paper",
        yref="paper",
        x=0,
        y=1.12,
        showarrow=False,
        font={"size": 12, "color": theme["muted_text"]},
        align="left",
    )
    fig.add_annotation(
        text="Myth: you must swing for max returns to beat the market. Reality: controlling volatility and costs often wins.",
        xref="paper",
        yref="paper",
        x=0,
        y=-0.24,
        showarrow=False,
        font={"size": 12, "color": theme["accent_alt"]},
        align="left",
    )

    fig.update_xaxes(title_text="Volatility (annualized %)", gridcolor=theme["grid"])
    fig.update_yaxes(title_text="Return (annualized %)", gridcolor=theme["grid"])

    return apply_layout(fig, theme)


def timeline_overlay_figure(
    sample: MarketSample, ticker: str, theme: Theme, horizon: int = 120
) -> go.Figure:
    """Overlay returns with period annotations to guide interpretation."""
    close_series = sample.history[ticker]["Close"].sort_index().tail(horizon)
    returns = close_series.pct_change().fillna(0)
    cumulative = (1 + returns).cumprod()
    rolling_vol = returns.rolling(20, min_periods=1).std() * np.sqrt(252)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=cumulative.index,
            y=cumulative,
            name="Growth of $1",
            line={"color": theme["accent"], "width": 2.2},
            hovertemplate="%{x|%Y-%m-%d}: %{y:.2f}x",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=rolling_vol.index,
            y=rolling_vol,
            name="Rolling Volatility",
            yaxis="y2",
            line={"color": theme["accent_alt"], "dash": "dot"},
            hovertemplate="%{x|%Y-%m-%d}: %{y:.2f}",
        )
    )

    if not close_series.empty:
        start, mid, end = (
            close_series.index[0],
            close_series.index[len(close_series) // 2],
            close_series.index[-1],
        )
        fig.add_vrect(
            x0=start, x1=mid, fillcolor=theme["panel"], opacity=0.08, line_width=0
        )
        fig.add_annotation(
            x=start,
            y=cumulative.max(),
            text="Accumulation phase: small edges compound.",
            showarrow=False,
            bgcolor=theme["panel"],
            font={"color": theme["text"]},
        )
        fig.add_annotation(
            x=end,
            y=cumulative.min(),
            text="Myth busting: timing every swing isn't necessary when discipline keeps you invested.",
            showarrow=True,
            arrowcolor=theme["accent_alt"],
            ay=-40,
            font={"color": theme["accent_alt"]},
        )

    fig.update_layout(
        yaxis={"title": "Growth multiple", "gridcolor": theme["grid"]},
        yaxis2={
            "title": "Volatility",
            "overlaying": "y",
            "side": "right",
            "showgrid": False,
        },
        legend={"orientation": "h", "y": 1.1},
    )
    fig.update_xaxes(title_text="Date", gridcolor=theme["grid"])

    return apply_layout(fig, theme)
