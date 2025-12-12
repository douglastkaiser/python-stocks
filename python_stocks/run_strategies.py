from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd

from .engine.simulator import SimulationEngine
from .services.strategy_service import StrategyResult

def run_some_strategies(
    initial_deposit: int,
    historic_data,
    enabled_strategies: Optional[List[str]] = None,
    parameter_overrides: Optional[Dict[str, Dict[str, Iterable[object]]]] = None,
) -> Tuple[pd.DataFrame, List[StrategyResult]]:
    engine = SimulationEngine(historic_data)
    output = engine.run_once(
        initial_deposit,
        enabled_strategies=enabled_strategies,
        parameter_overrides=parameter_overrides,
    )
    return output.report_df, output.results
