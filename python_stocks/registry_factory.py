"""Factory helpers for building strategy registries."""

from typing import Iterable

from .dougs_strategies import (
    strategy_buy_and_hold,
    strategy_maf_investment,
    strategy_marcus_2p25,
    strategy_no_investment,
    strategy_openclose_investment,
)
from .strategy_registry import Strategy, StrategyRegistry


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


__all__ = ["build_default_registry"]
