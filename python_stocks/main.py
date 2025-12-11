import time
from typing import Iterable, Optional

import matplotlib.pyplot as plt

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
) -> None:
    plt.close("all")
    start_time = time.time()

    stock_history_data = StockData(list(tickers))

    if start_date or end_date:
        stock_history_data.limit_timeframe(start_date, end_date)
    stock_history_data.add_external_investments(monthly_deposit, daily_deposit)

    run_some_strategies(initial_deposit, stock_history_data)

    stock_history_data.plot()

    end_time = time.time()
    print_time(end_time - start_time)

    plt.show()
