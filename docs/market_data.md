# Daily market data pipeline

## Source

`python_stocks.market_data.StooqDailyProvider` fetches end-of-day OHLCV data from Stooq's public CSV endpoint (no auth required).

## Curated symbols

Default refresh universe:

- `SPY`
- `DIA`
- `NDAQ`
- `TQQQ`

## Cadence

Run once per market day after close:

```bash
make ingest-daily
# or
PYTHONPATH=. python -m python_stocks ingest-daily
```

## Storage and fallback behavior

- Cached CSV location defaults to `${PYTHON_STOCKS_MARKET_DATA_DIR:-~/.cache/python-stocks/daily}`.
- During normal app loading, cached real-market files are used when available.
- If provider refresh fails, ingestion logs a warning and preserves existing cache.
- If cache is missing, simulations and dashboards continue using bundled demo CSVs in `python_stocks/raw_data`.

## Quality checks

Ingestion evaluates three quality gates and logs explicit warnings:

1. Missing business days in the local date range.
2. Stale datasets lagging expected latest business day.
3. Obvious malformed rows (invalid prices/ranges, negative volume, duplicate/unordered dates).
