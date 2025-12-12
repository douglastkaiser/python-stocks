"""Headless simulation engine for running trading strategies.

The engine isolates the simulation loop from presentation so it can be used by
batch processes and CI fixtures. It exposes deterministic runs controlled via
explicit seeds and supports rendering lightweight summary artifacts for
inspection.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd

from ..plotting import plt
from ..registry_factory import build_default_registry
from ..services.strategy_service import StrategyResult
from ..strategy_registry import Strategy, StrategyRegistry
from ..trading_history import TradingHistory


@dataclass(frozen=True)
class SimulationOutput:
    """Container bundling raw histories with normalized results."""

    report_df: pd.DataFrame
    results: List[StrategyResult]
    histories: List[TradingHistory]


def _format_parameters(parameters: Dict[str, object]) -> str:
    if not parameters:
        return "{}"
    return json.dumps(parameters, sort_keys=True)


def _compute_trade_counts(trading_history: TradingHistory, tracked_tickers: List[str]) -> int:
    position_changes = trading_history.trading_history_df[tracked_tickers].diff().fillna(0)
    return int((position_changes != 0).sum().sum())


def _tracking_error(portfolio_values: pd.Series, benchmark: pd.Series) -> float:
    benchmark_returns = benchmark.pct_change().dropna()
    portfolio_returns = portfolio_values.pct_change().dropna()
    aligned = portfolio_returns.align(benchmark_returns, join="inner")
    if aligned[0].empty or aligned[1].empty:
        return 0.0
    diff = aligned[0] - aligned[1]
    return float(diff.std() * np.sqrt(252))


def _compute_metrics(
    trading_history: TradingHistory,
    tracked_tickers: List[str],
    *,
    benchmark_ticker: Optional[str] = None,
    time_in_market_penalty_rate: float = 0.01,
) -> Dict[str, float]:
    portfolio_values = pd.Series(
        trading_history.portfolio_value_history(), index=trading_history.trading_history_df.index
    )
    returns = portfolio_values.pct_change().dropna()
    years = (
        (portfolio_values.index[-1] - portfolio_values.index[0]).days / 365.0
        if len(portfolio_values.index) > 1
        else 0
    )

    cagr = (portfolio_values.iloc[-1] / portfolio_values.iloc[0]) ** (1 / years) - 1 if years > 0 else 0
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = cumulative / running_max - 1
    max_drawdown = drawdown.min() if not drawdown.empty else 0

    volatility = returns.std() * (252 ** 0.5) if not returns.empty else 0
    sharpe = (returns.mean() * 252) / volatility if volatility else 0

    trade_counts = _compute_trade_counts(trading_history, tracked_tickers)

    positions = trading_history.trading_history_df[tracked_tickers]
    invested_days = int((positions.abs().sum(axis=1) > 0).sum()) if not positions.empty else 0
    time_in_market_ratio = invested_days / len(positions.index) if len(positions.index) else 0
    time_in_market_penalty = -time_in_market_ratio * time_in_market_penalty_rate

    benchmark_symbol = benchmark_ticker or (tracked_tickers[0] if tracked_tickers else None)
    benchmark_series = pd.Series(dtype=float)
    if benchmark_symbol and benchmark_symbol in trading_history.stock_df_to_today:
        benchmark_series = trading_history.stock_df_to_today[benchmark_symbol]["Close"].ffill()
    tracking_error = _tracking_error(portfolio_values, benchmark_series) if not benchmark_series.empty else 0.0

    return {
        "cagr": cagr,
        "max_drawdown": max_drawdown,
        "volatility": volatility,
        "sharpe_ratio": sharpe,
        "trade_count": trade_counts,
        "total_fees": trading_history.total_fees,
        "slippage_cost": trading_history.total_slippage_cost,
        "tracking_error": tracking_error,
        "time_in_market_ratio": time_in_market_ratio,
        "time_in_market_penalty": time_in_market_penalty,
    }


class SimulationEngine:
    """Batch-capable simulation engine with deterministic seeds."""

    def __init__(
        self,
        historic_data,
        *,
        registry: Optional[StrategyRegistry] = None,
        transaction_cost_rate: float = 0.0,
        slippage_pct: float = 0.0,
        benchmark_ticker: Optional[str] = None,
    ) -> None:
        self.historic_data = historic_data
        self.registry = registry
        self.transaction_cost_rate = max(0.0, transaction_cost_rate)
        self.slippage_pct = max(0.0, slippage_pct)
        self.benchmark_ticker = benchmark_ticker

    def _build_registry(self) -> StrategyRegistry:
        if self.registry is not None:
            return self.registry
        return build_default_registry(self.historic_data.tickers())

    def _seed(self, seed: Optional[int]) -> None:
        if seed is None:
            return
        random.seed(seed)
        np.random.seed(seed)

    def _build_histories(
        self,
        initial_deposit: int,
        registry: StrategyRegistry,
        enabled_strategies: Optional[List[str]],
        parameter_overrides: Optional[Dict[str, Dict[str, Iterable[object]]]],
    ) -> List[Tuple[TradingHistory, Strategy, Dict[str, object]]]:
        ticker_list = list(self.historic_data.tickers())

        ticker_list.append("bank_account")
        ticker_list.append("money_invested")

        strategy_runs = registry.expand_strategies(enabled_strategies, parameter_overrides)

        histories: List[Tuple[TradingHistory, Strategy, Dict[str, object]]] = []
        for strategy, params in strategy_runs:
            runner = strategy.build_runner(params)
            label = f"{strategy.name} {_format_parameters(params)}"
            history = TradingHistory(
                ticker_list,
                initial_deposit,
                runner,
                label,
                transaction_cost_rate=self.transaction_cost_rate,
                slippage_pct=self.slippage_pct,
            )
            histories.append((history, strategy, params))
        return histories

    def run_once(
        self,
        initial_deposit: int,
        *,
        enabled_strategies: Optional[List[str]] = None,
        parameter_overrides: Optional[Dict[str, Dict[str, Iterable[object]]]] = None,
        seed: Optional[int] = None,
    ) -> SimulationOutput:
        self._seed(seed)
        registry = self._build_registry()

        histories = self._build_histories(initial_deposit, registry, enabled_strategies, parameter_overrides)

        for row_n in range(1, self.historic_data.total_days()):
            stock_df_to_today, money_to_add = self.historic_data.get_stock_df_to_today_and_money_to_add(row_n)
            for history, _, _ in histories:
                history.new_day(stock_df_to_today, money_to_add)

        results: List[StrategyResult] = []
        tracked_tickers = list(self.historic_data.tickers())
        for history, strategy, params in histories:
            history.add_port_value_to_plt()
            history.printer()

            metrics = _compute_metrics(
                history,
                tracked_tickers,
                benchmark_ticker=self.benchmark_ticker,
            )
            results.append(
                StrategyResult(
                    strategy=strategy.name,
                    parameters=params,
                    cagr=metrics["cagr"],
                    max_drawdown=metrics["max_drawdown"],
                    volatility=metrics["volatility"],
                    sharpe_ratio=metrics["sharpe_ratio"],
                    trade_count=metrics["trade_count"],
                    total_fees=metrics["total_fees"],
                    slippage_cost=metrics["slippage_cost"],
                    tracking_error=metrics["tracking_error"],
                    time_in_market_penalty=metrics["time_in_market_penalty"],
                )
            )

        report_df = pd.DataFrame([result.as_dict() for result in results])
        return SimulationOutput(report_df=report_df, results=results, histories=[h for h, _, _ in histories])

    def run_batch(
        self,
        initial_deposit: int,
        *,
        seeds: Iterable[int],
        enabled_strategies: Optional[List[str]] = None,
        parameter_overrides: Optional[Dict[str, Dict[str, Iterable[object]]]] = None,
    ) -> List[SimulationOutput]:
        outputs: List[SimulationOutput] = []
        for seed in seeds:
            outputs.append(
                self.run_once(
                    initial_deposit,
                    enabled_strategies=enabled_strategies,
                    parameter_overrides=parameter_overrides,
                    seed=seed,
                )
            )
        return outputs


def render_summary_artifacts(output: SimulationOutput, output_dir: Path) -> Dict[str, Path]:
    """Generate deterministic summary artifacts for CI inspection.

    Returns a mapping of artifact type to file path.
    """

    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts: Dict[str, Path] = {}

    if not output.histories:
        return artifacts

    for history in output.histories:
        fig = plt.figure()
        plt.plot(history.trading_history_df.index, history.portfolio_value_history(), label=history.name)
        plt.legend()
        plt.title(f"Portfolio value - {history.name}")
        png_path = output_dir / f"{history.name}_portfolio.png"
        fig.savefig(png_path)
        plt.close(fig)
        artifacts[f"{history.name}_png"] = png_path

    html_path = output_dir / "simulation_summary.html"
    output.report_df.to_html(html_path, index=False)
    artifacts["summary_html"] = html_path

    return artifacts


__all__ = [
    "SimulationEngine",
    "SimulationOutput",
    "render_summary_artifacts",
]
