"""Reusable Plotly figures for the dashboard."""

from __future__ import annotations

import plotly.graph_objects as go

from python_stocks.dashboard.components.common import apply_layout
from python_stocks.dashboard.components.market import MarketSample
from python_stocks.dashboard.theme import Theme
from python_stocks.interactive_charts import _moving_average


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

    return apply_layout(fig, theme)


def strategy_signal_figure(
    sample: MarketSample, ticker: str, theme: Theme
) -> go.Figure:
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

    return apply_layout(fig, theme)


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

    return apply_layout(fig, theme)


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
    fig.update_layout(
        showlegend=False, annotations=[{"text": ticker, "font": {"size": 16}}]
    )
    return apply_layout(fig, theme)


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

    return apply_layout(fig, theme)
