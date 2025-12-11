from dataclasses import dataclass, field
from itertools import product
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from .trading_history import TradingHistory


StrategyCallable = Callable[[TradingHistory, Dict[str, Any]], TradingHistory]


@dataclass(frozen=True)
class Strategy:
    """A simple strategy interface with metadata and parameter sweeps."""

    name: str
    apply: StrategyCallable
    required_fields: Sequence[str] = field(default_factory=list)
    parameters: Dict[str, Sequence[Any]] = field(default_factory=dict)
    description: str = ""

    def expand_parameters(self, overrides: Optional[Dict[str, Iterable[Any]]] = None) -> List[Dict[str, Any]]:
        """Expand the parameter grid into a list of concrete parameter dictionaries."""

        overrides = overrides or {}
        param_values: Dict[str, List[Any]] = {}

        for param, default_values in self.parameters.items():
            override_values = overrides.get(param, default_values)
            if isinstance(override_values, (str, bytes)):
                param_values[param] = [override_values]
            else:
                param_values[param] = list(override_values)

        if not param_values:
            return [{}]

        keys, values = zip(*param_values.items())
        combinations = [dict(zip(keys, combo)) for combo in product(*values)]
        return combinations

    def build_runner(self, params: Dict[str, Any]) -> Callable[[TradingHistory], TradingHistory]:
        """Return a callable consumable by TradingHistory.new_day."""

        def runner(history: TradingHistory) -> TradingHistory:
            return self.apply(history, params)

        return runner


class StrategyRegistry:
    """Registry and expansion logic for running strategies."""

    def __init__(self) -> None:
        self._strategies: Dict[str, Strategy] = {}

    def register(self, strategy: Strategy) -> None:
        self._strategies[strategy.name] = strategy

    def available_strategies(self) -> List[str]:
        return list(self._strategies.keys())

    def get(self, name: str) -> Strategy:
        return self._strategies[name]

    def expand_strategies(
        self,
        enabled_names: Optional[Iterable[str]] = None,
        parameter_overrides: Optional[Dict[str, Dict[str, Iterable[Any]]]] = None,
    ) -> List[Tuple[Strategy, Dict[str, Any]]]:
        """Return all strategy/parameter combinations to run."""

        names = enabled_names or self.available_strategies()
        overrides = parameter_overrides or {}

        strategy_runs: List[Tuple[Strategy, Dict[str, Any]]] = []
        for name in names:
            if name not in self._strategies:
                continue
            strategy = self._strategies[name]
            for params in strategy.expand_parameters(overrides.get(name)):
                strategy_runs.append((strategy, params))

        return strategy_runs
