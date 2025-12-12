from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd

from .engine.simulator import SimulationEngine
from .services.strategy_service import StrategyResult
from .services.runtime_flags import prefer_cached_results


SimulationCacheKey = Tuple[
    int,
    Tuple[str, ...],
    Tuple[str, str, int],
    Tuple[str, ...],
    int,
    int,
]

_SIMULATION_CACHE: Dict[SimulationCacheKey, Tuple[pd.DataFrame, List[StrategyResult]]] = {}


def _normalize_overrides(parameter_overrides: Optional[Dict[str, Dict[str, Iterable[object]]]]) -> Tuple[str, ...]:
    if not parameter_overrides:
        return tuple()
    normalized = []
    for strategy, params in sorted(parameter_overrides.items()):
        flattened_params = [f"{param}={tuple(values)}" for param, values in sorted(params.items())]
        normalized.append(f"{strategy}:{'|'.join(flattened_params)}")
    return tuple(normalized)


def _build_cache_key(
    initial_deposit: int,
    historic_data,
    enabled_strategies: Optional[List[str]],
    parameter_overrides: Optional[Dict[str, Dict[str, Iterable[object]]]],
) -> SimulationCacheKey:
    tickers = tuple(historic_data.tickers())
    idx = historic_data.data_frame.index
    window = (str(idx[0]), str(idx[-1]), len(idx))
    enabled = tuple(enabled_strategies) if enabled_strategies else tuple()
    overrides = _normalize_overrides(parameter_overrides)
    return (
        initial_deposit,
        tickers + enabled,
        window,
        overrides,
        historic_data.monthly_deposit,
        historic_data.daily_deposit,
    )

def run_some_strategies(
    initial_deposit: int,
    historic_data,
    enabled_strategies: Optional[List[str]] = None,
    parameter_overrides: Optional[Dict[str, Dict[str, Iterable[object]]]] = None,
    prefer_cache: Optional[bool] = None,
) -> Tuple[pd.DataFrame, List[StrategyResult]]:
    cache_key = _build_cache_key(initial_deposit, historic_data, enabled_strategies, parameter_overrides)
    use_cache = prefer_cached_results(prefer_cache)

    if use_cache and cache_key in _SIMULATION_CACHE:
        cached_df, cached_results = _SIMULATION_CACHE[cache_key]
        return cached_df.copy(deep=True), list(cached_results)

    engine = SimulationEngine(historic_data)
    output = engine.run_once(
        initial_deposit,
        enabled_strategies=enabled_strategies,
        parameter_overrides=parameter_overrides,
    )

    if use_cache:
        _SIMULATION_CACHE[cache_key] = (output.report_df.copy(deep=True), list(output.results))

    return output.report_df, output.results
