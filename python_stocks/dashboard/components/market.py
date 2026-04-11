"""Market sample scaffolding used across interactive components."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List

import numpy as np
import pandas as pd


@dataclass
class MarketSample:
    """Container describing the demo price history."""

    tickers: List[str]
    history: pd.DataFrame
    data_source: str = "Unknown source"
    market_date: pd.Timestamp = field(default_factory=lambda: pd.Timestamp.utcnow())
    last_refresh: pd.Timestamp = field(
        default_factory=lambda: pd.Timestamp.now(tz="UTC")
    )

    @classmethod
    def demo(cls, tickers: Iterable[str], periods: int = 180) -> "MarketSample":
        end_date = pd.offsets.BDay().rollback(pd.Timestamp.today().normalize())
        index = pd.date_range(end=end_date, periods=periods, freq="B")
        frames = {}
        for ticker in tickers:
            noise = pd.Series(np.random.normal(0, 1.2, periods), index=index).cumsum()
            drift = pd.Series(np.linspace(0.1, 4, periods), index=index)
            close = (100 + noise + drift).apply(lambda v: max(1, v))
            frames[ticker] = pd.DataFrame(
                {"Close": close, "Volume": (close * 1_000).round(0)}, index=index
            )
        return cls(
            tickers=list(tickers),
            history=pd.concat(frames, axis=1),
            data_source="Demo market sample (simulated OHLCV)",
            market_date=end_date,
            last_refresh=pd.Timestamp.now(tz="UTC").floor("s"),
        )

    def is_stale(
        self, *, now: pd.Timestamp | None = None, stale_after_hours: int = 24
    ) -> bool:
        """Whether the dataset refresh timestamp is older than the threshold."""
        now_ts = now or pd.Timestamp.now(tz="UTC")
        refresh_ts = self.last_refresh
        if refresh_ts.tzinfo is None:
            refresh_ts = refresh_ts.tz_localize("UTC")
        return (now_ts - refresh_ts) > pd.Timedelta(hours=stale_after_hours)
