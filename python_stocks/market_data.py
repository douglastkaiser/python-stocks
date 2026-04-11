"""Daily market data ingestion and quality checks for curated symbols."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
import os
from pathlib import Path
from typing import Protocol, Sequence

import pandas as pd

from .data_loading import load_into_stock_data_set

LOGGER = logging.getLogger(__name__)

CURATED_TICKERS: tuple[str, ...] = ("SPY", "DIA", "NDAQ", "TQQQ")
DEFAULT_STALE_AFTER_BUSINESS_DAYS = 3
_STOOQ_URL = "https://stooq.com/q/d/l/?s={symbol}.us&i=d"


class DailyOhlcvProvider(Protocol):
    """Provider abstraction for external daily OHLCV data."""

    def fetch_daily_ohlcv(
        self,
        symbol: str,
        *,
        start: pd.Timestamp | None = None,
        end: pd.Timestamp | None = None,
    ) -> pd.DataFrame:
        """Return daily OHLCV rows with Date/Open/High/Low/Close/Volume columns."""


class StooqDailyProvider:
    """Fetch end-of-day OHLCV quotes from stooq.com's public CSV endpoint."""

    def fetch_daily_ohlcv(
        self,
        symbol: str,
        *,
        start: pd.Timestamp | None = None,
        end: pd.Timestamp | None = None,
    ) -> pd.DataFrame:
        url = _STOOQ_URL.format(symbol=symbol.lower())
        frame = pd.read_csv(url)
        if frame.empty:
            raise ValueError(f"No rows returned from Stooq for {symbol}.")

        frame["Date"] = pd.to_datetime(frame["Date"], errors="raise")
        frame = frame[["Date", "Open", "High", "Low", "Close", "Volume"]]
        frame = frame.sort_values("Date")

        if start is not None:
            frame = frame[frame["Date"] >= start]
        if end is not None:
            frame = frame[frame["Date"] <= end]

        return frame.reset_index(drop=True)


class DailyPriceStore:
    """Local CSV store for curated daily OHLCV data."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or default_market_data_dir()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, ticker: str) -> Path:
        return self.root / f"{ticker.upper()}.csv"

    def exists(self, ticker: str) -> bool:
        return self._path(ticker).exists()

    def load(self, ticker: str) -> pd.DataFrame:
        if not self.exists(ticker):
            raise FileNotFoundError(
                f"No cached market data exists for {ticker} in {self.root}"
            )
        return load_into_stock_data_set(ticker.upper(), data_dir=self.root)

    def save(self, ticker: str, frame: pd.DataFrame) -> Path:
        path = self._path(ticker)
        frame.to_csv(path, index=False)
        return path


@dataclass
class DataQualityReport:
    missing_business_days: list[str] = field(default_factory=list)
    stale_business_days: int = 0
    malformed_records: list[str] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(
            self.missing_business_days
            or self.stale_business_days
            or self.malformed_records
        )


@dataclass
class IngestionResult:
    ticker: str
    source: str
    updated_rows: int
    total_rows: int
    data_path: Path | None
    quality: DataQualityReport
    status: str
    message: str


def default_market_data_dir() -> Path:
    configured = os.getenv("PYTHON_STOCKS_MARKET_DATA_DIR", "").strip()
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".cache" / "python-stocks" / "daily"


def evaluate_data_quality(
    frame: pd.DataFrame,
    *,
    now: datetime | None = None,
    stale_after_business_days: int = DEFAULT_STALE_AFTER_BUSINESS_DAYS,
) -> DataQualityReport:
    report = DataQualityReport()
    if frame.empty:
        report.malformed_records.append("dataset is empty")
        return report

    indexed = frame.copy()
    if "Date" in indexed.columns:
        indexed["Date"] = pd.to_datetime(indexed["Date"], errors="coerce")
        indexed = indexed.set_index("Date")

    if indexed.index.isna().any():
        report.malformed_records.append("found rows with invalid date values")
        indexed = indexed[~indexed.index.isna()]

    if indexed.index.has_duplicates:
        report.malformed_records.append("duplicate date rows are present")

    if not indexed.index.is_monotonic_increasing:
        report.malformed_records.append("date index is not increasing")

    for column in ("Open", "High", "Low", "Close"):
        if column not in indexed.columns:
            report.malformed_records.append(f"missing required OHLC column: {column}")
            return report

    if "Volume" not in indexed.columns:
        report.malformed_records.append("missing required volume column: Volume")
        return report

    negative_price_mask = (indexed[["Open", "High", "Low", "Close"]] <= 0).any(axis=1)
    if negative_price_mask.any():
        report.malformed_records.append(
            f"{int(negative_price_mask.sum())} rows contain non-positive prices"
        )

    high_low_mask = indexed["High"] < indexed["Low"]
    if high_low_mask.any():
        report.malformed_records.append(
            f"{int(high_low_mask.sum())} rows have High lower than Low"
        )

    ohlc_out_of_range = (
        (indexed["Open"] > indexed["High"])
        | (indexed["Open"] < indexed["Low"])
        | (indexed["Close"] > indexed["High"])
        | (indexed["Close"] < indexed["Low"])
    )
    if ohlc_out_of_range.any():
        report.malformed_records.append(
            f"{int(ohlc_out_of_range.sum())} rows have Open/Close outside High-Low range"
        )

    negative_volume = indexed["Volume"] < 0
    if negative_volume.any():
        report.malformed_records.append(
            f"{int(negative_volume.sum())} rows contain negative volume"
        )

    if len(indexed.index) > 1:
        expected = pd.bdate_range(indexed.index.min(), indexed.index.max())
        missing = expected.difference(indexed.index)
        if len(missing) > 0:
            report.missing_business_days = [d.strftime("%Y-%m-%d") for d in missing]

    ref_now = now or datetime.now(timezone.utc)
    ref_date = pd.Timestamp(ref_now.date())
    latest_expected = (
        ref_date if ref_date.dayofweek < 5 else ref_date - pd.offsets.BDay(1)
    )
    latest_expected = pd.Timestamp(latest_expected).normalize()
    last_date = pd.Timestamp(indexed.index.max()).normalize()

    if latest_expected > last_date:
        stale_days = len(
            pd.bdate_range(last_date + pd.offsets.BDay(1), latest_expected)
        )
        if stale_days >= stale_after_business_days:
            report.stale_business_days = stale_days

    return report


def _normalize_for_store(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = frame.copy()
    normalized["Date"] = pd.to_datetime(normalized["Date"], errors="raise")
    normalized = normalized.sort_values("Date").drop_duplicates(
        subset=["Date"], keep="last"
    )
    normalized = normalized[["Date", "Close", "Open", "High", "Low", "Volume"]]
    return normalized.reset_index(drop=True)


def _merge_frames(
    existing: pd.DataFrame | None, incoming: pd.DataFrame
) -> pd.DataFrame:
    normalized_incoming = _normalize_for_store(incoming)
    if existing is None:
        return normalized_incoming

    existing_csv = existing.reset_index().rename(columns={"index": "Date"})
    existing_csv = existing_csv[["Date", "Close", "Open", "High", "Low", "Volume"]]
    combined = pd.concat([existing_csv, normalized_incoming], ignore_index=True)
    combined["Date"] = pd.to_datetime(combined["Date"], errors="raise")
    combined = combined.sort_values("Date").drop_duplicates(
        subset=["Date"], keep="last"
    )
    return combined.reset_index(drop=True)


def ingest_curated_daily_data(
    *,
    tickers: Sequence[str] = CURATED_TICKERS,
    provider: DailyOhlcvProvider | None = None,
    store: DailyPriceStore | None = None,
    stale_after_business_days: int = DEFAULT_STALE_AFTER_BUSINESS_DAYS,
    full_refresh: bool = False,
) -> list[IngestionResult]:
    provider = provider or StooqDailyProvider()
    store = store or DailyPriceStore()

    results: list[IngestionResult] = []
    for ticker in tickers:
        upper = ticker.upper()
        existing: pd.DataFrame | None = None
        if store.exists(upper):
            try:
                existing = store.load(upper)
            except Exception as exc:  # pragma: no cover - defensive logging path
                LOGGER.warning("Failed to load existing cache for %s: %s", upper, exc)

        start: pd.Timestamp | None = None
        if existing is not None and not existing.empty and not full_refresh:
            start = pd.Timestamp(existing.index.max()) + pd.offsets.BDay(1)

        try:
            incoming = provider.fetch_daily_ohlcv(upper, start=start)
            merged = _merge_frames(existing, incoming)
            quality = evaluate_data_quality(
                merged,
                stale_after_business_days=stale_after_business_days,
            )
            data_path = store.save(upper, merged)

            if quality.malformed_records:
                status = "warning"
                message = f"{upper}: malformed records detected ({'; '.join(quality.malformed_records)})"
                LOGGER.warning(message)
            elif quality.missing_business_days:
                status = "warning"
                preview = ", ".join(quality.missing_business_days[:3])
                message = (
                    f"{upper}: missing {len(quality.missing_business_days)} business days; "
                    f"first missing dates: {preview}"
                )
                LOGGER.warning(message)
            elif quality.stale_business_days:
                status = "warning"
                message = f"{upper}: dataset is stale by {quality.stale_business_days} business days"
                LOGGER.warning(message)
            else:
                status = "ok"
                message = f"{upper}: updated {len(incoming)} rows"
                LOGGER.info(message)

            results.append(
                IngestionResult(
                    ticker=upper,
                    source="provider",
                    updated_rows=len(incoming),
                    total_rows=len(merged),
                    data_path=data_path,
                    quality=quality,
                    status=status,
                    message=message,
                )
            )
        except Exception as exc:
            if existing is not None:
                quality = evaluate_data_quality(
                    existing.reset_index().rename(columns={"index": "Date"}),
                    stale_after_business_days=stale_after_business_days,
                )
                message = f"{upper}: provider failed ({exc}); using cached data at {store._path(upper)}"
                LOGGER.warning(message)
                results.append(
                    IngestionResult(
                        ticker=upper,
                        source="cache",
                        updated_rows=0,
                        total_rows=len(existing),
                        data_path=store._path(upper),
                        quality=quality,
                        status="warning",
                        message=message,
                    )
                )
                continue

            message = (
                f"{upper}: provider failed ({exc}) and no local cache exists. "
                "Dashboard/demo will continue using bundled raw_data fallback."
            )
            LOGGER.error(message)
            results.append(
                IngestionResult(
                    ticker=upper,
                    source="fallback",
                    updated_rows=0,
                    total_rows=0,
                    data_path=None,
                    quality=DataQualityReport(),
                    status="error",
                    message=message,
                )
            )

    return results


def load_market_or_demo_dataset(
    ticker: str,
    *,
    market_data_dir: Path | None = None,
    demo_data_dir: Path | None = None,
) -> pd.DataFrame:
    """Load real-data cache when present, otherwise bundled demo CSV."""

    market_store = DailyPriceStore(root=market_data_dir)
    upper = ticker.upper()
    if market_store.exists(upper):
        return market_store.load(upper)

    fallback_dir = demo_data_dir or Path(__file__).resolve().parent / "raw_data"
    return load_into_stock_data_set(upper, data_dir=fallback_dir)


__all__ = [
    "CURATED_TICKERS",
    "DEFAULT_STALE_AFTER_BUSINESS_DAYS",
    "DailyOhlcvProvider",
    "DataQualityReport",
    "DailyPriceStore",
    "IngestionResult",
    "StooqDailyProvider",
    "default_market_data_dir",
    "evaluate_data_quality",
    "ingest_curated_daily_data",
    "load_market_or_demo_dataset",
]
