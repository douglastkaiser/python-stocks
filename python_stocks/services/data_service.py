"""Utilities for loading price history with caching hooks."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Callable, Dict, Iterable, Optional

import pandas as pd

from ..data_loading import load_into_stock_data_set
from ..stock_data import StockData


class DataService:
    """Provide cached access to bundled CSVs or external fetchers.

    The service wraps ``load_into_stock_data_set`` and ``StockData`` to avoid
    repeated disk reads when multiple components request the same ticker.
    """

    def __init__(self, data_dir: Optional[Path] = None) -> None:
        self.data_dir = data_dir or Path(__file__).resolve().parent.parent / "raw_data"
        self._dataset_cache: Dict[str, pd.DataFrame] = {}

    def clear_cache(self) -> None:
        """Drop any cached DataFrame copies."""

        self._dataset_cache.clear()
        self._cached_loader.cache_clear()

    def load_dataset(
        self,
        ticker: str,
        *,
        fetcher: Optional[Callable[[str], pd.DataFrame]] = None,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """Return a copy of the validated dataset for ``ticker``.

        Results are cached by ticker symbol unless ``force_refresh`` is set.
        """

        if force_refresh or ticker not in self._dataset_cache:
            df = load_into_stock_data_set(ticker, data_dir=self.data_dir, fetcher=fetcher)
            self._dataset_cache[ticker] = df
        return self._dataset_cache[ticker].copy(deep=True)

    def build_stock_data(
        self,
        tickers: Iterable[str],
        *,
        monthly_deposit: int = 0,
        daily_deposit: int = 0,
    ) -> StockData:
        """Create a ``StockData`` instance backed by cached loaders."""

        loader = self._cached_loader
        return StockData(list(tickers), monthly_deposit, daily_deposit, loader=loader)

    @lru_cache(maxsize=32)
    def _cached_loader(self, ticker: str) -> pd.DataFrame:
        """Lazily cache datasets for use inside :class:`StockData`."""

        return self.load_dataset(ticker)


__all__ = ["DataService"]
