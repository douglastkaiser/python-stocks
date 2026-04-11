from datetime import datetime, timezone

import pandas as pd

from python_stocks.market_data import (
    DailyPriceStore,
    evaluate_data_quality,
    ingest_curated_daily_data,
)


class _FakeProvider:
    def __init__(self, frame: pd.DataFrame):
        self.frame = frame

    def fetch_daily_ohlcv(self, symbol: str, *, start=None, end=None):
        frame = self.frame.copy()
        if start is not None:
            frame = frame[frame["Date"] >= start]
        if end is not None:
            frame = frame[frame["Date"] <= end]
        return frame


class _FailingProvider:
    def fetch_daily_ohlcv(self, symbol: str, *, start=None, end=None):
        raise RuntimeError("provider unavailable")


def _frame_with_business_days(start: str, periods: int) -> pd.DataFrame:
    dates = pd.bdate_range(start=start, periods=periods)
    return pd.DataFrame(
        {
            "Date": dates,
            "Open": [100.0 + i for i in range(periods)],
            "High": [101.0 + i for i in range(periods)],
            "Low": [99.0 + i for i in range(periods)],
            "Close": [100.5 + i for i in range(periods)],
            "Volume": [1000 + i for i in range(periods)],
        }
    )


def test_ingest_happy_path_updates_store(tmp_path):
    provider = _FakeProvider(_frame_with_business_days("2025-01-06", 5))
    store = DailyPriceStore(root=tmp_path)

    results = ingest_curated_daily_data(
        tickers=["SPY"],
        provider=provider,
        store=store,
        stale_after_business_days=10000,
    )

    assert len(results) == 1
    result = results[0]
    assert result.status == "ok"
    assert result.updated_rows == 5
    assert result.total_rows == 5
    assert (tmp_path / "SPY.csv").exists()


def test_ingest_uses_cached_data_when_provider_fails(tmp_path):
    seeded = _frame_with_business_days("2025-01-06", 3)
    DailyPriceStore(root=tmp_path).save("SPY", seeded)

    results = ingest_curated_daily_data(
        tickers=["SPY"],
        provider=_FailingProvider(),
        store=DailyPriceStore(root=tmp_path),
    )

    assert results[0].source == "cache"
    assert "using cached data" in results[0].message


def test_quality_flags_missing_and_stale_data():
    frame = (
        _frame_with_business_days("2025-01-06", 5)
        .drop(index=[2])
        .reset_index(drop=True)
    )
    report = evaluate_data_quality(
        frame,
        now=datetime(2025, 1, 20, tzinfo=timezone.utc),
        stale_after_business_days=2,
    )

    assert "2025-01-08" in report.missing_business_days
    assert report.stale_business_days >= 2


def test_quality_flags_malformed_records():
    frame = _frame_with_business_days("2025-01-06", 2)
    frame.loc[0, "High"] = 90
    frame.loc[1, "Volume"] = -1

    report = evaluate_data_quality(frame)

    assert report.malformed_records
    assert any("High lower than Low" in item for item in report.malformed_records)
    assert any("negative volume" in item for item in report.malformed_records)
