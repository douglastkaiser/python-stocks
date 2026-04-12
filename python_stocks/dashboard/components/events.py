"""Event detection and annotation helpers for dashboard figures."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

import pandas as pd

from python_stocks.dashboard.theme import Theme


@dataclass(frozen=True)
class DashboardEvent:
    """Structured event metadata used for chart callouts."""

    kind: str
    timestamp: pd.Timestamp
    label: str
    value: float | None = None
    strength: float | None = None
    details: dict[str, Any] = field(default_factory=dict)


def _enforce_datetime_index(series: pd.Series) -> pd.Series:
    if not isinstance(series.index, pd.DatetimeIndex):
        raise ValueError("Event detection requires a DatetimeIndex.")
    return series.sort_index().dropna()


def _thin_events(
    events: Sequence[DashboardEvent], min_spacing: int = 7
) -> list[DashboardEvent]:
    if not events:
        return []
    selected: list[DashboardEvent] = []
    for event in sorted(events, key=lambda item: item.timestamp):
        if not selected:
            selected.append(event)
            continue
        if (event.timestamp - selected[-1].timestamp) >= pd.Timedelta(days=min_spacing):
            selected.append(event)
            continue
        prev_strength = abs(selected[-1].strength or 0.0)
        curr_strength = abs(event.strength or 0.0)
        if curr_strength > prev_strength:
            selected[-1] = event
    return selected


def detect_regime_shifts(
    close_series: pd.Series,
    *,
    return_window: int = 10,
    vol_window: int = 20,
    min_spacing: int = 10,
) -> list[DashboardEvent]:
    """Detect transitions across rolling return/volatility states."""
    close = _enforce_datetime_index(close_series)
    returns = close.pct_change().dropna()
    if len(returns) < max(return_window, vol_window) + 2:
        return []

    rolling_return = returns.rolling(return_window).mean()
    rolling_vol = returns.rolling(vol_window).std()
    baseline_return = rolling_return.rolling(60, min_periods=15).median()
    baseline_vol = rolling_vol.rolling(60, min_periods=15).median()

    state_frame = pd.DataFrame(
        {
            "return": rolling_return,
            "vol": rolling_vol,
            "baseline_return": baseline_return,
            "baseline_vol": baseline_vol,
        }
    ).dropna()
    if state_frame.empty:
        return []

    ret_state = state_frame["return"] >= state_frame["baseline_return"]
    vol_state = state_frame["vol"] >= state_frame["baseline_vol"]
    regime = ret_state.astype(int).astype(str) + vol_state.astype(int).astype(str)
    changed = regime != regime.shift(1)

    label_map = {
        "00": "Regime: defensive drift",
        "01": "Regime: stressed tape",
        "10": "Regime: low-vol grind",
        "11": "Regime: momentum burst",
    }

    events: list[DashboardEvent] = []
    for ts in regime[changed.fillna(False)].index:
        row = state_frame.loc[ts]
        ret_delta = row["return"] - row["baseline_return"]
        vol_delta = row["vol"] - row["baseline_vol"]
        events.append(
            DashboardEvent(
                kind="regime_shift",
                timestamp=ts,
                label=label_map.get(regime.loc[ts], "Regime shift"),
                value=float(row["return"]),
                strength=float(abs(ret_delta) + abs(vol_delta)),
                details={"regime_code": regime.loc[ts]},
            )
        )
    return _thin_events(events, min_spacing=min_spacing)


def detect_drawdown_inflections(
    close_series: pd.Series, *, slope_window: int = 5, min_spacing: int = 7
) -> list[DashboardEvent]:
    """Detect sign changes in drawdown slope as inflection points."""
    close = _enforce_datetime_index(close_series)
    if len(close) < slope_window + 3:
        return []

    drawdown = close / close.cummax() - 1
    slope = drawdown.diff().rolling(slope_window, min_periods=2).mean()
    sign = slope.apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    sign_change = (sign != sign.shift(1)) & sign.ne(0) & sign.shift(1).ne(0)
    threshold = slope.abs().quantile(0.6)

    events: list[DashboardEvent] = []
    for ts in slope[sign_change.fillna(False)].index:
        slope_val = float(slope.loc[ts])
        if abs(slope_val) < threshold:
            continue
        label = "Drawdown stabilizing" if slope_val > 0 else "Drawdown accelerating"
        events.append(
            DashboardEvent(
                kind="drawdown_inflection",
                timestamp=ts,
                label=label,
                value=float(drawdown.loc[ts]),
                strength=abs(slope_val),
            )
        )

    return _thin_events(events, min_spacing=min_spacing)


def detect_turnover_spikes(
    volume_series: pd.Series,
    *,
    percentile: float = 0.95,
    lookback: int = 60,
    min_spacing: int = 5,
) -> list[DashboardEvent]:
    """Detect volume percentile spikes as a turnover proxy."""
    volume = _enforce_datetime_index(volume_series)
    if len(volume) < lookback:
        return []

    rolling_rank = volume.rolling(lookback, min_periods=max(10, lookback // 3)).apply(
        lambda x: pd.Series(x).rank(pct=True).iloc[-1],
        raw=False,
    )
    candidates = rolling_rank[rolling_rank >= percentile].dropna()

    events: list[DashboardEvent] = []
    for ts, rank in candidates.items():
        events.append(
            DashboardEvent(
                kind="turnover_spike",
                timestamp=ts,
                label="Turnover spike",
                value=float(volume.loc[ts]),
                strength=float(rank),
                details={"percentile": float(rank)},
            )
        )
    return _thin_events(events, min_spacing=min_spacing)


def default_events_for_series(
    close_series: pd.Series, volume_series: pd.Series
) -> list[DashboardEvent]:
    """Generate a merged, chronologically sorted event set."""
    merged = [
        *detect_regime_shifts(close_series),
        *detect_drawdown_inflections(close_series),
        *detect_turnover_spikes(volume_series),
    ]
    return sorted(merged, key=lambda event: event.timestamp)


def event_style(kind: str, theme: Theme) -> dict[str, str]:
    if kind == "regime_shift":
        return {"color": theme["accent"], "symbol": "diamond"}
    if kind == "turnover_spike":
        return {"color": theme["accent_alt"], "symbol": "triangle-up"}
    return {"color": theme["muted_text"], "symbol": "circle"}


def concise_event_labels(events: Iterable[DashboardEvent], limit: int = 3) -> str:
    listed = list(events)[:limit]
    if not listed:
        return "No major events detected in window."
    return " • ".join(
        f"{event.timestamp:%b %d}: {event.label.replace('Regime: ', '')}"
        for event in listed
    )


def make_event_annotations(
    events: Iterable[DashboardEvent],
    theme: Theme,
    *,
    y_lookup: dict[pd.Timestamp, float] | None = None,
    xref: str = "x",
    yref: str = "y",
    ay: int = -28,
    limit: int = 4,
) -> list[dict[str, Any]]:
    """Create standardized Plotly annotations for event callouts."""
    annotations: list[dict[str, Any]] = []
    for event in list(events)[:limit]:
        y_value = None
        if y_lookup:
            y_value = y_lookup.get(event.timestamp)
        if y_value is None:
            continue
        style = event_style(event.kind, theme)
        annotations.append(
            {
                "x": event.timestamp,
                "y": y_value,
                "xref": xref,
                "yref": yref,
                "text": event.label,
                "showarrow": True,
                "arrowhead": 2,
                "arrowcolor": style["color"],
                "ax": 0,
                "ay": ay,
                "bgcolor": theme["panel"],
                "bordercolor": style["color"],
                "borderwidth": 1,
                "font": {"size": 11, "color": theme["text"]},
            }
        )
    return annotations
