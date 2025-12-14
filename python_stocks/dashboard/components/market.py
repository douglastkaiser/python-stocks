"""Market sample scaffolding used across interactive components."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

import numpy as np
import pandas as pd


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
            noise = pd.Series(np.random.normal(0, 1.2, periods), index=index).cumsum()
            drift = pd.Series(np.linspace(0.1, 4, periods), index=index)
            close = (100 + noise + drift).apply(lambda v: max(1, v))
            frames[ticker] = pd.DataFrame(
                {"Close": close, "Volume": (close * 1_000).round(0)}, index=index
            )
        return cls(tickers=list(tickers), history=pd.concat(frames, axis=1))
