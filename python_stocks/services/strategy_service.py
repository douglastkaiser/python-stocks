"""Typed interfaces for strategy configuration and results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from ..trading_history import TradingHistory


@dataclass(frozen=True)
class StrategyContext:
    """Standard input passed to each strategy implementation."""

    history: TradingHistory
    params: Dict[str, Any]


@dataclass(frozen=True)
class StrategyConfig:
    """Serializable configuration for wiring strategies in UI callbacks."""

    name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "parameters": dict(self.parameters),
            "enabled": self.enabled,
        }


@dataclass(frozen=True)
class StrategyResult:
    """Normalized output from a completed strategy simulation."""

    strategy: str
    parameters: Dict[str, Any]
    cagr: float
    max_drawdown: float
    volatility: float
    sharpe_ratio: float
    trade_count: int
    total_fees: float
    slippage_cost: float
    tracking_error: float
    time_in_market_penalty: float

    def as_dict(self) -> Dict[str, Any]:
        return {
            "strategy": self.strategy,
            "parameters": dict(self.parameters),
            "cagr": self.cagr,
            "max_drawdown": self.max_drawdown,
            "volatility": self.volatility,
            "sharpe_ratio": self.sharpe_ratio,
            "trade_count": self.trade_count,
            "total_fees": self.total_fees,
            "slippage_cost": self.slippage_cost,
            "tracking_error": self.tracking_error,
            "time_in_market_penalty": self.time_in_market_penalty,
        }


__all__ = ["StrategyConfig", "StrategyContext", "StrategyResult"]
