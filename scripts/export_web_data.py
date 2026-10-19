"""Export validated, explicitly historical price snapshots for the static app."""

from __future__ import annotations

import csv
import json
import math
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYMBOLS = {
    "SPY": "S&P 500 ETF",
    "DIA": "Dow Jones ETF",
    "NDAQ": "Nasdaq, Inc.",
    "TQQQ": "3× Nasdaq-100 ETF",
}


def export(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for ticker, name in SYMBOLS.items():
        with (ROOT / "python_stocks" / "raw_data" / f"{ticker}.csv").open() as source:
            rows = list(csv.DictReader(source))
        prices = []
        previous = ""
        for row in rows:
            session = date.fromisoformat(row["Date"]).isoformat()
            # Adjusted closes account for splits and distributions in this snapshot.
            close = float(row["Adj Close"])
            if session <= previous or not math.isfinite(close) or close <= 0:
                raise ValueError(f"Invalid or unordered price in {ticker}: {session}")
            prices.append({"date": session, "close": close})
            previous = session
        if not prices:
            raise ValueError(f"Empty history for {ticker}")
        payload = {
            "ticker": ticker,
            "name": name,
            "source": "Bundled historical CSV · adjusted close",
            "mode": "historical",
            "start": prices[0]["date"],
            "end": prices[-1]["date"],
            "prices": prices,
        }
        (output / f"{ticker}.json").write_text(
            json.dumps(payload, separators=(",", ":")) + "\n"
        )


if __name__ == "__main__":
    export(ROOT / "web" / "public" / "data")
