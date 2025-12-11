import time
from pathlib import Path
from typing import Iterable, Optional

from .plotting import plt

from .math_helper import print_time
from .interactive_charts import export_interactive_price_charts
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
    report_dir: Optional[str] = None,
    show_plots: bool = True,
) -> None:
    plt.close("all")
    start_time = time.time()
    portfolio_fig = plt.figure()
    portfolio_fig.suptitle("Portfolio performance")

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

    if report_dir:
        report_path = Path(report_dir)
        assets_path = report_path / "assets"
        assets_path.mkdir(parents=True, exist_ok=True)

        report_df.to_csv(report_path / "strategy_summary.csv", index=False)
        report_df.to_json(report_path / "strategy_summary.json", orient="records", indent=2)

        for idx, fig_num in enumerate(sorted(plt.get_fignums()), start=1):
            fig = plt.figure(fig_num)
            fig.savefig(assets_path / f"figure_{idx}.png", bbox_inches="tight", metadata={"Date": None})

        export_interactive_price_charts(stock_history_data.tickers(), stock_history_data.data_frame, assets_path)

    end_time = time.time()
    print_time(end_time - start_time)

    if show_plots:
        plt.show()
