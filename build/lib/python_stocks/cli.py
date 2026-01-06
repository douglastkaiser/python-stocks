import argparse
from typing import Dict, List, Optional

from .main import run_simulation


DEFAULT_TICKERS = ["SPY"]
DEFAULT_START_DATE = "2015-01-01"
DEFAULT_END_DATE = "2019-01-01"
DEFAULT_INITIAL_DEPOSIT = 50_000
DEFAULT_DAILY_DEPOSIT = 0
DEFAULT_MONTHLY_DEPOSIT = 0


def _parse_value(value: str):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def _parse_parameter_overrides(
    raw_overrides: List[str],
) -> Dict[str, Dict[str, List[object]]]:
    overrides: Dict[str, Dict[str, List[object]]] = {}
    for raw in raw_overrides:
        if "=" not in raw or "." not in raw:
            continue
        lhs, rhs = raw.split("=", 1)
        strategy_name, param_name = lhs.split(".", 1)
        values = [_parse_value(value) for value in rhs.split(",") if value]
        if not values:
            continue
        overrides.setdefault(strategy_name, {})[param_name] = values
    return overrides


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
    run_parser.add_argument(
        "--start",
        dest="start_date",
        default=DEFAULT_START_DATE,
        help="Start date (YYYY-MM-DD)",
    )
    run_parser.add_argument(
        "--end", dest="end_date", default=DEFAULT_END_DATE, help="End date (YYYY-MM-DD)"
    )
    run_parser.add_argument(
        "--initial",
        dest="initial_deposit",
        type=int,
        default=DEFAULT_INITIAL_DEPOSIT,
        help="Initial deposit",
    )
    run_parser.add_argument(
        "--daily",
        dest="daily_deposit",
        type=int,
        default=DEFAULT_DAILY_DEPOSIT,
        help="Daily deposit amount",
    )
    run_parser.add_argument(
        "--monthly",
        dest="monthly_deposit",
        type=int,
        default=DEFAULT_MONTHLY_DEPOSIT,
        help="Monthly deposit amount",
    )
    run_parser.add_argument(
        "--strategies",
        nargs="+",
        default=None,
        help="Registered strategies to run (default: all)",
    )
    run_parser.add_argument(
        "--param",
        dest="parameter_overrides",
        action="append",
        default=[],
        help="Strategy parameter sweep overrides of the form strategy.param=1,2,3",
    )
    run_parser.add_argument(
        "--report-dir",
        dest="report_dir",
        default=None,
        help="Directory to write static reports (CSV/JSON) and saved plots for GitHub Pages hosting",
    )
    run_parser.add_argument(
        "--no-show",
        dest="show_plots",
        action="store_false",
        help="Skip interactive plot display (useful for GitHub Pages artifact generation)",
    )

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
            strategies=args.strategies,
            parameter_overrides=_parse_parameter_overrides(args.parameter_overrides),
            report_dir=args.report_dir,
            show_plots=args.show_plots,
        )


if __name__ == "__main__":
    main()
