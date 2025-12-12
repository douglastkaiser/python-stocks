"""Dashboard components package."""
from python_stocks.dashboard.components.comparison import comparison_matrix_figure, timeline_overlay_figure
from python_stocks.dashboard.components.education import guidance_tooltips, myth_busting_callouts
from python_stocks.dashboard.components.figures import (
    cost_impact_figure,
    diagnostics_figure,
    price_trend_figure,
    strategy_signal_figure,
    time_in_market_figure,
)
from python_stocks.dashboard.components.market import MarketSample

__all__ = [
    "MarketSample",
    "price_trend_figure",
    "strategy_signal_figure",
    "cost_impact_figure",
    "time_in_market_figure",
    "diagnostics_figure",
    "comparison_matrix_figure",
    "timeline_overlay_figure",
    "guidance_tooltips",
    "myth_busting_callouts",
]
