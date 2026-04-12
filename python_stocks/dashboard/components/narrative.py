"""Narrative models and metric-driven narrative helpers."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ChartNarrative:
    """Short chart explanation rendered in a fixed three-row layout."""

    what_changed: str
    why_it_matters: str
    what_to_watch_next: str


def _clean_series(series: pd.Series) -> pd.Series:
    return series.sort_index().dropna()


def _annualized_volatility(close: pd.Series, window: int = 20) -> float:
    returns = close.pct_change().dropna()
    if returns.empty:
        return 0.0
    return float(returns.tail(window).std() * (252**0.5))


def _drawdown(close: pd.Series) -> pd.Series:
    running_peak = close.cummax()
    return (close / running_peak) - 1


def _turnover_proxy(close: pd.Series) -> pd.Series:
    return close.pct_change().abs().rolling(5, min_periods=2).mean()


def build_market_narrative(
    close: pd.Series,
    volume: pd.Series,
    *,
    cost_bps: int,
    label: str,
) -> ChartNarrative:
    """Build concise narrative copy from close/volume series and cost assumptions."""
    close = _clean_series(close)
    volume = _clean_series(volume).reindex(close.index).ffill().bfill()
    if len(close) < 5:
        return ChartNarrative(
            what_changed=f"{label}: Insufficient history for a reliable trend read.",
            why_it_matters="Limited data means confidence bands are wide.",
            what_to_watch_next="Wait for more observations before changing exposure.",
        )

    ma_fast = close.rolling(10, min_periods=3).mean()
    ma_slow = close.rolling(50, min_periods=10).mean()
    spread_now = float((ma_fast - ma_slow).iloc[-1] / close.iloc[-1])
    spread_prev = float((ma_fast - ma_slow).shift(10).iloc[-1] / close.iloc[-1])

    lookback = min(20, len(close) - 1)
    trailing_return = float(close.iloc[-1] / close.iloc[-lookback] - 1)
    spread_delta = spread_now - spread_prev
    what_changed = (
        f"{label}: Close {trailing_return:+.1%}/{lookback}d; "
        f"MA spread {spread_now:+.1%} ({spread_delta:+.1%})."
    )

    vol_20 = _annualized_volatility(close, window=20)
    cost_drag = vol_20 * (cost_bps / 10_000)
    why_it_matters = (
        f"Vol {vol_20:.1%} ann.; {cost_bps} bps cost trims edge ~{cost_drag:.2%}/yr."
    )

    returns = close.pct_change().dropna()
    vol_60 = (
        float(returns.tail(60).std() * (252**0.5)) if len(returns) >= 10 else vol_20
    )
    drawdown = _drawdown(close)
    drawdown_now = float(drawdown.iloc[-1])
    drawdown_20 = float(drawdown.tail(20).min())

    turnover = _turnover_proxy(close)
    turnover_ratio = float(turnover.iloc[-1] / max(turnover.tail(20).median(), 1e-9))
    volume_ratio = float(volume.iloc[-1] / max(volume.tail(20).median(), 1.0))

    alerts = []
    if vol_20 > vol_60 * 1.12:
        alerts.append(f"rolling vol up ({vol_20:.1%}>{vol_60:.1%})")
    if drawdown_now <= drawdown_20 - 0.01:
        alerts.append(f"drawdown widening ({drawdown_now:.1%})")
    if turnover_ratio > 1.35 or volume_ratio > 1.6:
        alerts.append(
            f"turnover proxy spike ({max(turnover_ratio, volume_ratio):.2f}x)"
        )

    watch_tail = (
        "; ".join(alerts)
        if alerts
        else "signals stable; monitor for fresh breakout or churn"
    )
    what_to_watch_next = f"Watch: {watch_tail}."

    return ChartNarrative(
        what_changed=what_changed,
        why_it_matters=why_it_matters,
        what_to_watch_next=what_to_watch_next,
    )
