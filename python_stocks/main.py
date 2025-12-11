import time
from typing import Iterable, Optional

from .plotting import plt

from .math_helper import print_time
from .run_strategies import run_some_strategies
from .stock_data import StockData


def run_simulation(
    tickers: Iterable[str],
    start_date: Optional[str],
    end_date: Optional[str],
    initial_deposit: int,
    daily_deposit: int,
    monthly_deposit: int,
    strategies: Optional[Iterable[str]] = None,
    parameter_overrides: Optional[dict] = None,
) -> None:
    plt.close("all")
    start_time = time.time()

    stock_history_data = StockData(list(tickers))

    if start_date or end_date:
        stock_history_data.limit_timeframe(start_date, end_date)
    stock_history_data.add_external_investments(monthly_deposit, daily_deposit)

    report_df, _ = run_some_strategies(
        initial_deposit,
        stock_history_data,
        enabled_strategies=list(strategies) if strategies else None,
        parameter_overrides=parameter_overrides,
    )

    if not report_df.empty:
        print("\nStrategy performance summary:\n", report_df)

    stock_history_data.plot()

    end_time = time.time()
    print_time(end_time - start_time)

    plt.show()
