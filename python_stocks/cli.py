import argparse
from typing import List, Optional

from .main import run_simulation


DEFAULT_TICKERS = ["SPY"]
DEFAULT_START_DATE = "2015-01-01"
DEFAULT_END_DATE = "2019-01-01"
DEFAULT_INITIAL_DEPOSIT = 50_000
DEFAULT_DAILY_DEPOSIT = 0
DEFAULT_MONTHLY_DEPOSIT = 0


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="python_stocks")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run trading strategy simulations")
    run_parser.add_argument(
        "--tickers",
        nargs="+",
        default=DEFAULT_TICKERS,
        help="Ticker symbols to simulate",
    )
    run_parser.add_argument("--start", dest="start_date", default=DEFAULT_START_DATE, help="Start date (YYYY-MM-DD)")
    run_parser.add_argument("--end", dest="end_date", default=DEFAULT_END_DATE, help="End date (YYYY-MM-DD)")
    run_parser.add_argument("--initial", dest="initial_deposit", type=int, default=DEFAULT_INITIAL_DEPOSIT, help="Initial deposit")
    run_parser.add_argument("--daily", dest="daily_deposit", type=int, default=DEFAULT_DAILY_DEPOSIT, help="Daily deposit amount")
    run_parser.add_argument("--monthly", dest="monthly_deposit", type=int, default=DEFAULT_MONTHLY_DEPOSIT, help="Monthly deposit amount")

    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)

    if args.command == "run":
        run_simulation(
            tickers=args.tickers,
            start_date=args.start_date,
            end_date=args.end_date,
            initial_deposit=args.initial_deposit,
            daily_deposit=args.daily_deposit,
            monthly_deposit=args.monthly_deposit,
        )


if __name__ == "__main__":
    main()
