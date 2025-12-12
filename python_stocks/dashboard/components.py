"""Reusable Plotly components for the dashboard."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from python_stocks.dashboard.theme import Theme
from python_stocks.interactive_charts import _moving_average
from python_stocks.plotting import TEST_MODE_FLAG


@dataclass
class MarketSample:
    """Container describing the demo price history."""

    tickers: List[str]
    history: pd.DataFrame

    @classmethod
    def demo(cls, tickers: Iterable[str], periods: int = 180) -> "MarketSample":
        index = pd.date_range(end=pd.Timestamp.today(), periods=periods, freq="B")
        frames = {}
        for ticker in tickers:
            noise = pd.Series(np.random.normal(0, 1.2, periods)).cumsum()
            drift = pd.Series(np.linspace(0.1, 4, periods), index=index)
            close = (100 + noise + drift).apply(lambda v: max(1, v))
            frames[ticker] = pd.DataFrame({"Close": close, "Volume": (close * 1_000).round(0)})
        return cls(tickers=list(tickers), history=pd.concat(frames, axis=1))


def _apply_layout(fig: go.Figure, theme: Theme) -> go.Figure:
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


def price_trend_figure(sample: MarketSample, ticker: str, theme: Theme) -> go.Figure:
    close_series = sample.history[ticker]["Close"].sort_index()
    ma10 = _moving_average(close_series, 10)
    ma100 = _moving_average(close_series, 100)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=close_series.index,
            y=close_series,
            name=f"{ticker} Close",
            mode="lines",
            line={"color": theme["accent"], "width": 2.4},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=ma10.index,
            y=ma10,
            name="10d MA",
            mode="lines",
            line={"color": theme["accent_alt"], "dash": "dot"},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=ma100.index,
            y=ma100,
            name="100d MA",
            mode="lines",
            line={"color": theme["text"], "dash": "dash"},
        )
    )

    fig.update_yaxes(title_text="Price ($)", gridcolor=theme["grid"])
    fig.update_xaxes(title_text="Date", gridcolor=theme["grid"])

    return _apply_layout(fig, theme)


def strategy_signal_figure(sample: MarketSample, ticker: str, theme: Theme) -> go.Figure:
    close_series = sample.history[ticker]["Close"].sort_index()
    ma_short = _moving_average(close_series, 20)
    ma_long = _moving_average(close_series, 60)
    signal = (ma_short > ma_long).astype(int)
    returns = close_series.pct_change().fillna(0)
    strat_returns = (signal.shift(1).fillna(0) * returns).cumsum() * 100
    buy_hold = returns.cumsum() * 100

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=close_series.index,
            y=strat_returns,
            name="MA Crossover Strategy",
            mode="lines",
            line={"color": theme["accent"]},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=close_series.index,
            y=buy_hold,
            name="Buy & Hold",
            mode="lines",
            line={"color": theme["accent_alt"], "dash": "dash"},
        )
    )

    fig.update_yaxes(title_text="Cumulative Return (%)", gridcolor=theme["grid"])
    fig.update_xaxes(title_text="Date", gridcolor=theme["grid"])

    return _apply_layout(fig, theme)


def cost_impact_figure(sample: MarketSample, ticker: str, theme: Theme) -> go.Figure:
    volume = sample.history[ticker]["Volume"].tail(60)
    cost_basis = volume / volume.max()
    impact = (volume.rank(pct=True) * 0.4) + 0.1

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=volume.index,
            y=cost_basis,
            name="Liquidity (scaled)",
            marker_color=theme["accent"],
            opacity=0.8,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=impact.index,
            y=impact,
            name="Estimated Impact",
            mode="lines+markers",
            marker={"color": theme["accent_alt"], "size": 6},
            line={"shape": "spline", "color": theme["accent_alt"]},
            yaxis="y2",
        )
    )

    fig.update_layout(
        yaxis={"title": "Scaled Volume", "gridcolor": theme["grid"]},
        yaxis2={
            "title": "Slippage %",
            "overlaying": "y",
            "side": "right",
            "showgrid": False,
            "tickformat": ".1%",
        },
    )
    fig.update_xaxes(gridcolor=theme["grid"])

    return _apply_layout(fig, theme)


def time_in_market_figure(sample: MarketSample, ticker: str, theme: Theme) -> go.Figure:
    close_series = sample.history[ticker]["Close"].sort_index()
    trend = close_series.diff().fillna(0)
    positive = (trend > 0).sum()
    negative = (trend <= 0).sum()
    active_ratio = positive / (positive + negative)

    fig = go.Figure(
        data=[
            go.Pie(
                labels=["In Market", "On Sidelines"],
                values=[active_ratio, 1 - active_ratio],
                hole=0.55,
                marker={"colors": [theme["accent"], theme["panel"]]},
                textinfo="label+percent",
            )
        ]
    )
    fig.update_layout(showlegend=False, annotations=[{"text": ticker, "font": {"size": 16}}])
    return _apply_layout(fig, theme)


def diagnostics_figure(sample: MarketSample, ticker: str, theme: Theme) -> go.Figure:
    close_series = sample.history[ticker]["Close"].sort_index()
    returns = close_series.pct_change().dropna() * 100

    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=returns,
            nbinsx=30,
            marker_color=theme["accent"],
            opacity=0.85,
            name="Daily Returns",
        )
    )

    fig.update_xaxes(title_text="Daily Return (%)", gridcolor=theme["grid"])
    fig.update_yaxes(title_text="Frequency", gridcolor=theme["grid"])

    return _apply_layout(fig, theme)
