"""Refresh curated daily market data cache."""

from python_stocks.cli import main


if __name__ == "__main__":
    main(["ingest-daily"])
