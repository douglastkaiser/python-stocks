import json
from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd

from .plotting import plt

from .dougs_strategies import (
    strategy_buy_and_hold,
    strategy_maf_investment,
    strategy_marcus_2p25,
    strategy_no_investment,
    strategy_openclose_investment,
)
from .strategy_registry import Strategy, StrategyRegistry
from .trading_history import TradingHistory


def build_default_registry(available_tickers: Iterable[str]) -> StrategyRegistry:
    registry = StrategyRegistry()

    registry.register(
        Strategy(
            name="no_investment",
            apply=strategy_no_investment,
            description="Hold cash with no trades.",
        )
    )

    registry.register(
        Strategy(
            name="buy_and_hold",
            apply=strategy_buy_and_hold,
            required_fields=["Close"],
            parameters={"ticker": list(available_tickers)},
            description="Buy all shares in a ticker and hold.",
        )
    )

    registry.register(
        Strategy(
            name="open_close",
            apply=strategy_openclose_investment,
            required_fields=["Open", "Close"],
            parameters={"ticker": list(available_tickers)},
            description="Buy or sell at open based on previous close.",
        )
    )

    registry.register(
        Strategy(
            name="moving_average_filter",
            apply=strategy_maf_investment,
            required_fields=["Close"],
            parameters={
                "ticker": list(available_tickers),
                "short_window": [10, 20],
                "long_window": [100, 200],
            },
            description="Moving average filter crossover with slope checks.",
        )
    )

    registry.register(
        Strategy(
            name="marcus_savings",
            apply=strategy_marcus_2p25,
            parameters={"interest_rate": [2.25]},
            description="Simple Marcus savings account style accrual.",
        )
    )

    return registry


def _format_parameters(parameters: Dict[str, object]) -> str:
    if not parameters:
        return "{}"
    return json.dumps(parameters, sort_keys=True)


def _compute_trade_counts(trading_history: TradingHistory, tracked_tickers: List[str]) -> int:
    position_changes = trading_history.trading_history_df[tracked_tickers].diff().fillna(0)
    return int((position_changes != 0).sum().sum())


def _compute_metrics(trading_history: TradingHistory, tracked_tickers: List[str]) -> Dict[str, float]:
    portfolio_values = pd.Series(trading_history.portfolio_value_history(), index=trading_history.trading_history_df.index)
    returns = portfolio_values.pct_change().dropna()
    years = (portfolio_values.index[-1] - portfolio_values.index[0]).days / 365.0 if len(portfolio_values.index) > 1 else 0

    cagr = (portfolio_values.iloc[-1] / portfolio_values.iloc[0]) ** (1 / years) - 1 if years > 0 else 0
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = cumulative / running_max - 1
    max_drawdown = drawdown.min() if not drawdown.empty else 0

    volatility = returns.std() * (252 ** 0.5) if not returns.empty else 0
    sharpe = (returns.mean() * 252) / volatility if volatility else 0

    trade_counts = _compute_trade_counts(trading_history, tracked_tickers)

    return {
        "cagr": cagr,
        "max_drawdown": max_drawdown,
        "volatility": volatility,
        "sharpe_ratio": sharpe,
        "trade_count": trade_counts,
    }


def run_some_strategies(
    initial_deposit: int,
    historic_data,
    enabled_strategies: Optional[List[str]] = None,
    parameter_overrides: Optional[Dict[str, Dict[str, Iterable[object]]]] = None,
) -> Tuple[pd.DataFrame, List[Dict[str, object]]]:
    ticker_list = list(historic_data.tickers())
    tracked_tickers = list(ticker_list)

    ticker_list.append("bank_account")
    ticker_list.append("money_invested")

    registry = build_default_registry(tracked_tickers)
    strategy_runs = registry.expand_strategies(enabled_strategies, parameter_overrides)

    th_list: List[Tuple[TradingHistory, Strategy, Dict[str, object]]] = []
    for strategy, params in strategy_runs:
        runner = strategy.build_runner(params)
        label = f"{strategy.name} {_format_parameters(params)}"
        th_list.append((TradingHistory(ticker_list, initial_deposit, runner, label), strategy, params))

    for row_n in range(1, historic_data.total_days()):
        stock_df_to_today, money_to_add = historic_data.get_stock_df_to_today_and_money_to_add(row_n)
        for th, _, _ in th_list:
            th.new_day(stock_df_to_today, money_to_add)

    report_rows: List[Dict[str, object]] = []
    for th, strategy, params in th_list:
        th.add_port_value_to_plt()
        th.printer()

        metrics = _compute_metrics(th, tracked_tickers)
        report_rows.append(
            {
                "strategy": strategy.name,
                "parameters": params,
                **metrics,
            }
        )

    report_df = pd.DataFrame(report_rows)
    return report_df, report_df.to_dict(orient="records")
