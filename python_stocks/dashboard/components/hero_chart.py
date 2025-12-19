"""Hero strategy comparison chart for the dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from python_stocks.dashboard.components.common import apply_layout
from python_stocks.dashboard.theme import Theme
from python_stocks.interactive_charts import _moving_average


@dataclass(frozen=True)
class StrategySeries:
    name: str
    cumulative_return: pd.Series
    time_in_market: float


def _buy_hold(returns: pd.Series) -> StrategySeries:
    cumulative = (1 + returns).cumprod()
    return StrategySeries(
        name="Buy & Hold",
        cumulative_return=cumulative,
        time_in_market=1.0,
    )


def _trend_follow(series: pd.Series, returns: pd.Series) -> StrategySeries:
    ma_short = _moving_average(series, 20)
    ma_long = _moving_average(series, 60)
    signal = (ma_short > ma_long).astype(float).reindex(series.index).fillna(0.0)
    strategy_returns = returns * signal.shift(1).fillna(0.0)
    cumulative = (1 + strategy_returns).cumprod()
    return StrategySeries(
        name="Trend Filter (20/60 MA)",
        cumulative_return=cumulative,
        time_in_market=float(signal.mean()),
    )


def _vol_target(returns: pd.Series) -> StrategySeries:
    rolling_vol = returns.rolling(20, min_periods=1).std() * np.sqrt(252)
    target_vol = 0.15
    exposure = (target_vol / rolling_vol).clip(upper=1.0).fillna(1.0)
    strategy_returns = returns * exposure.shift(1).fillna(0.0)
    cumulative = (1 + strategy_returns).cumprod()
    time_in_market = float((exposure > 0.05).mean())
    return StrategySeries(
        name="Volatility Target (15%)",
        cumulative_return=cumulative,
        time_in_market=time_in_market,
    )


def _strategy_catalog(series: pd.Series, returns: pd.Series) -> Dict[str, StrategySeries]:
    return {
        "Buy & Hold": _buy_hold(returns),
        "Trend Filter (20/60 MA)": _trend_follow(series, returns),
        "Volatility Target (15%)": _vol_target(returns),
    }


def _normalize_selection(
    primary: str, comparisons: Iterable[str], available: Iterable[str]
) -> List[str]:
    available_set = list(available)
    selected = [primary] if primary in available_set else []
    selected.extend([item for item in comparisons if item in available_set])
    deduped = list(dict.fromkeys(selected))
    if len(deduped) < 3:
        for strategy in available_set:
            if strategy not in deduped:
                deduped.append(strategy)
            if len(deduped) >= 3:
                break
    return deduped


def strategy_hero_figure(
    price_history: pd.DataFrame,
    theme: Theme,
    *,
    primary_strategy: str,
    comparison_strategies: Iterable[str],
    timeframe: int,
) -> go.Figure:
    series = price_history["Close"].sort_index()
    if timeframe:
        series = series.tail(timeframe)
    returns = series.pct_change().fillna(0.0)
    catalog = _strategy_catalog(series, returns)
    selection = _normalize_selection(
        primary_strategy, comparison_strategies, catalog.keys()
    )
    fig = go.Figure()

    for strategy_name in selection:
        strategy = catalog[strategy_name]
        fig.add_trace(
            go.Scatter(
                x=strategy.cumulative_return.index,
                y=(strategy.cumulative_return - 1) * 100,
                name=strategy.name,
                mode="lines",
                line={
                    "width": 3 if strategy_name == primary_strategy else 2,
                    "color": theme["accent"]
                    if strategy_name == primary_strategy
                    else theme["accent_alt"],
                },
                customdata=[strategy.time_in_market * 100] * len(
                    strategy.cumulative_return
                ),
                hovertemplate=(
                    "%{x|%Y-%m-%d}<br>"
                    "%{y:.1f}% cumulative return<br>"
                    "Time in market: %{customdata:.0f}%<extra></extra>"
                ),
            )
        )

    rolling_vol = returns.rolling(20, min_periods=1).std() * np.sqrt(252) * 100
    fig.add_trace(
        go.Scatter(
            x=rolling_vol.index,
            y=rolling_vol,
            name="Rolling Volatility",
            yaxis="y2",
            line={"color": theme["text"], "dash": "dot"},
            hovertemplate="%{x|%Y-%m-%d}<br>%{y:.2f}% annualized<extra></extra>",
        )
    )

    primary_time = catalog.get(primary_strategy, catalog["Buy & Hold"]).time_in_market
    fig.add_annotation(
        text=(
            f"Time in market lesson: {primary_time:.0%} invested keeps compounding alive, "
            "even when returns look noisy."
        ),
        xref="paper",
        yref="paper",
        x=0,
        y=1.16,
        showarrow=False,
        font={"size": 12, "color": theme["muted_text"]},
        align="left",
    )
    fig.add_annotation(
        text="Explore deeper trade-offs in the <a href='#comparison-tab'>Comparisons tab</a>.",
        xref="paper",
        yref="paper",
        x=0,
        y=-0.22,
        showarrow=False,
        font={"size": 12, "color": theme["accent_alt"]},
        align="left",
    )

    fig.update_layout(
        yaxis={"title": "Cumulative return (%)", "gridcolor": theme["grid"]},
        yaxis2={
            "title": "Volatility (annualized %)",
            "overlaying": "y",
            "side": "right",
            "showgrid": False,
        },
        legend={"orientation": "h", "y": 1.08},
    )
    fig.update_xaxes(title_text="Date", gridcolor=theme["grid"])

    return apply_layout(fig, theme)


__all__ = ["strategy_hero_figure"]
