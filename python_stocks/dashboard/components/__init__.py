"""Dashboard components package."""

from python_stocks.dashboard.components.comparison import (
    comparison_matrix_figure,
    timeline_overlay_figure,
)
from python_stocks.dashboard.components.education import (
    guidance_tooltips,
    metric_callouts,
)
from python_stocks.dashboard.components.layout import (
    button_link,
    chart_narrative_block,
    data_provenance_panel,
    hero_banner,
    kpi_stat,
    muted_text,
    page_header,
    pill,
    responsive_grid,
    section_header,
    section_block,
    surface_card,
    text_stack,
)
from python_stocks.dashboard.components.figures import (
    cost_impact_figure,
    diagnostics_figure,
    price_trend_figure,
    strategy_signal_figure,
    time_in_market_figure,
)
from python_stocks.dashboard.components.market import MarketSample
from python_stocks.dashboard.components.narrative import (
    ChartNarrative,
    build_market_narrative,
)

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
    "metric_callouts",
    "surface_card",
    "text_stack",
    "chart_narrative_block",
    "ChartNarrative",
    "build_market_narrative",
    "button_link",
    "data_provenance_panel",
    "page_header",
    "pill",
    "muted_text",
    "responsive_grid",
    "section_header",
    "section_block",
    "hero_banner",
    "kpi_stat",
]
