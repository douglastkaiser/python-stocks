"""Dash dashboard entrypoint for python-stocks."""

from __future__ import annotations

from typing import Dict, List

import pandas as pd
from dash import Dash, Input, Output, State, dcc, html, no_update

from python_stocks.dashboard.components import (
    ChartNarrative,
    MarketSample,
    build_market_narrative,
    button_link,
    chart_narrative_block,
    comparison_matrix_figure,
    cost_impact_figure,
    data_provenance_panel,
    diagnostics_figure,
    guidance_tooltips,
    hero_banner,
    kpi_stat,
    myth_busting_callouts,
    muted_text,
    page_header,
    responsive_grid,
    section_block,
    surface_card,
    text_stack,
    price_trend_figure,
    strategy_signal_figure,
    time_in_market_figure,
    timeline_overlay_figure,
)
from python_stocks.dashboard.theme import (
    DEFAULT_THEME_KEY,
    get_theme,
    page_style,
    surface_style,
)

_SAMPLE = MarketSample.demo(["AAPL", "MSFT", "SPY", "QQQ"])
_CHART_IDS = [
    "hero-comparison-chart",
    "price-chart",
    "strategy-chart",
    "cost-impact-chart",
    "time-in-market-chart",
    "diagnostics-chart",
    "price-chart-secondary",
    "strategy-chart-secondary",
    "cost-impact-chart-secondary",
    "comparison-matrix",
    "timeline-overlay",
    "price-spotlight",
    "strategy-spotlight",
    "cost-spotlight",
    "matrix-spotlight",
    "timeline-spotlight",
]
_HERO_PRESETS = {
    "balanced": {"label": "Balanced (90d / 25bps drag)", "window": 90, "cost_bps": 25},
    "fast": {"label": "Fast swings (45d / 10bps)", "window": 45, "cost_bps": 10},
    "patient": {"label": "Patient (140d / 40bps)", "window": 140, "cost_bps": 40},
}
SCENARIO_PRESETS = {
    "rangebound": {
        "title": "Rangebound week",
        "description": "QQQ chopping sideways; tighten the lookback and keep costs lean.",
        "ticker": "QQQ",
        "window": 60,
        "cost_bps": 15,
        "horizon": 60,
        "hero_preset": "fast",
    },
    "pullback": {
        "title": "Pullback recovery",
        "description": "MSFT digesting gains; slower window with higher drag to avoid churn.",
        "ticker": "MSFT",
        "window": 130,
        "cost_bps": 35,
        "horizon": 252,
        "hero_preset": "patient",
    },
    "breakout": {
        "title": "Breakout attempt",
        "description": "AAPL re-accelerating; medium window with balanced costs.",
        "ticker": "AAPL",
        "window": 90,
        "cost_bps": 25,
        "horizon": 120,
        "hero_preset": "balanced",
    },
}
STRATEGY_SUMMARIES = [
    {
        "title": "Trend-following crossover",
        "headline": "+8.2% excess vs. buy & hold",
        "detail": "Shorter lookbacks adapt quickly while cost guardrails keep churn contained.",
    },
    {
        "title": "Cost-aware rebalance",
        "headline": "0.35% slippage budget",
        "detail": "Only rotates when expected drag is offset by signal strength.",
    },
    {
        "title": "Volatility targeting",
        "headline": "Stays 62% invested through chop",
        "detail": "Keeps compounding intact by sizing down during noisy swings instead of exiting entirely.",
    },
]
WORKFLOW_STEPS = [
    {
        "title": "Anchor to market regime",
        "body": "Frame the current move before changing parameters so confidence reflects context, not recency bias.",
    },
    {
        "title": "Adjust cost sensitivity",
        "body": "Increase or decrease drag assumptions to see when expected edge no longer clears execution friction.",
    },
    {
        "title": "Confirm tradeoff profile",
        "body": "Validate return, drawdown, and participation tradeoffs before promoting a rule to live monitoring.",
    },
]
SIMULATION_FEED = [
    {
        "name": "MA crossover 20/80",
        "result": "+6.1% vs. benchmark",
        "note": "Costs capped at 20 bps; recovered faster after shallow pullbacks.",
    },
    {
        "name": "Equal-weight rotation",
        "result": "Tracking within 0.2%",
        "note": "Held through volatility, reducing cash drag across six weeks of chop.",
    },
    {
        "name": "Low-vol filter",
        "result": "Max drawdown -7.8%",
        "note": "Stayed invested but resized positions to absorb overlapping signals.",
    },
]
SPOTLIGHT_LABELS = {
    "price-spotlight": "Price replay",
    "strategy-spotlight": "Signal spread",
    "matrix-spotlight": "Scenario matrix",
    "timeline-spotlight": "Timeline path",
    "cost-spotlight": "Cost sensitivity",
}


def _build_card(
    title: str, body: List[html.Div | dcc.Graph], theme_key: str
) -> html.Div:
    return surface_card(theme_key=theme_key, title=title, children=body)


def _graph_container(graph_id: str, label: str, height: str) -> html.Div:
    return html.Div(
        role="img",
        **{"aria-label": label},
        children=[
            dcc.Graph(
                id=graph_id,
                config={"displayModeBar": False},
                style={"height": height},
            ),
            html.Div(id=f"{graph_id}-metadata"),
        ],
    )


def _format_timestamp(ts: pd.Timestamp) -> str:
    return ts.strftime("%Y-%m-%d %H:%M:%S UTC")


def _build_chart_metadata(
    *,
    theme_key: str,
    ticker: str,
    window: int,
    cost_bps: int,
    horizon: int,
    hero_ticker: str,
    hero_preset: str,
    sample: MarketSample,
) -> Dict[str, html.Div]:
    market_date = sample.market_date.strftime("%Y-%m-%d")
    refresh_time = _format_timestamp(sample.last_refresh)
    is_stale = sample.is_stale(stale_after_hours=24)
    shared_scope = f"window {window}d · cost {cost_bps} bps · horizon {horizon}d"
    chart_scopes = {
        "hero-comparison-chart": f"hero preset {hero_preset}",
        "price-chart": shared_scope,
        "strategy-chart": shared_scope,
        "cost-impact-chart": shared_scope,
        "time-in-market-chart": shared_scope,
        "diagnostics-chart": shared_scope,
        "price-chart-secondary": shared_scope,
        "strategy-chart-secondary": shared_scope,
        "cost-impact-chart-secondary": shared_scope,
        "comparison-matrix": shared_scope,
        "timeline-overlay": shared_scope,
        "price-spotlight": shared_scope,
        "strategy-spotlight": shared_scope,
        "cost-spotlight": shared_scope,
        "matrix-spotlight": shared_scope,
        "timeline-spotlight": shared_scope,
    }
    chart_tickers = {chart_id: ticker for chart_id in _CHART_IDS}
    chart_tickers["hero-comparison-chart"] = hero_ticker or ticker
    return {
        f"{chart_id}-metadata": data_provenance_panel(
            theme_key=theme_key,
            data_source=sample.data_source,
            market_date=market_date,
            last_refresh=refresh_time,
            ticker=chart_tickers[chart_id],
            scope_label=chart_scopes[chart_id],
            is_stale=is_stale,
        )
        for chart_id in _CHART_IDS
    }


def _overview_tab(theme_key: str) -> html.Div:
    return html.Div(
        className="tab-grid tab-grid--two",
        children=[
            _build_card(
                "Price Overview",
                [_graph_container("price-chart", "Price overview chart", "360px")],
                theme_key,
            ),
            _build_card(
                "Strategy Lab",
                [
                    html.P("Moving average crossover vs. buy and hold."),
                    _graph_container(
                        "strategy-chart", "Strategy lab performance chart", "360px"
                    ),
                ],
                theme_key,
            ),
        ],
    )


def _kpi_hero(theme_key: str) -> html.Div:
    theme = get_theme(theme_key)
    hero_kpis = [
        kpi_stat(
            label="Benchmark discipline",
            value="92% time in-market",
            caption="Signals prefer participation over predictions.",
            theme_key=theme_key,
        ),
        kpi_stat(
            label="Drag minimized",
            value="< 40 bps modeled",
            caption="Liquidity guardrails keep live trades close to the model.",
            theme_key=theme_key,
        ),
        kpi_stat(
            label="Compare faster",
            value="Sub-second refresh",
            caption="Strategy Lab and Compare views respond as soon as you tweak inputs.",
            theme_key=theme_key,
        ),
    ]
    toggle_group_style = {
        "display": "flex",
        "flexDirection": "column",
        "gap": "8px",
        "padding": "10px 12px",
        "borderRadius": "12px",
        "background": f"rgba(15,23,42,{0.05 if theme['mode']=='light' else 0.35})",
        "border": f"1px solid {theme['grid']}",
    }
    radio_label_style = {
        "padding": "12px 12px",
        "borderRadius": "10px",
        "border": f"1px solid {theme['grid']}",
        "marginRight": "6px",
        "display": "inline-flex",
        "alignItems": "center",
        "minHeight": "44px",
        "gap": "6px",
        "background": f"rgba(148, 163, 184, {0.15 if theme['mode']=='light' else 0.18})",
        "cursor": "pointer",
    }
    quick_toggles = html.Div(
        [
            html.Div(
                [
                    html.Span("Quick ticker", style={"fontWeight": 700}),
                    html.Span(
                        "See how the matrix shifts between watchlist names.",
                        style=muted_text(theme) | {"fontSize": "12px"},
                    ),
                    dcc.RadioItems(
                        id="hero-ticker-toggle",
                        options=[
                            {"label": ticker, "value": ticker}
                            for ticker in _SAMPLE.tickers
                        ],
                        value=_SAMPLE.tickers[0],
                        inline=True,
                        inputStyle={"marginRight": "6px"},
                        labelStyle=radio_label_style,
                    ),
                ],
                style=toggle_group_style,
            ),
            html.Div(
                [
                    html.Span("Preset windows", style={"fontWeight": 700}),
                    html.Span(
                        "Pick a window + cost pairing to compare reactions.",
                        style=muted_text(theme) | {"fontSize": "12px"},
                    ),
                    dcc.RadioItems(
                        id="hero-preset-toggle",
                        options=[
                            {"label": preset["label"], "value": key}
                            for key, preset in _HERO_PRESETS.items()
                        ],
                        value="balanced",
                        inline=True,
                        inputStyle={"marginRight": "6px"},
                        labelStyle=radio_label_style,
                    ),
                ],
                style=toggle_group_style,
            ),
        ],
        className="hero-quick-toggles",
        style={"display": "flex", "gap": "10px", "flexWrap": "wrap"},
    )
    hero_visual = html.Div(
        style=surface_style(theme) | {"display": "flex", "flexDirection": "column"},
        children=[
            html.Div(
                [
                    html.Div(
                        "Live comparison chart",
                        style={"fontWeight": 700, "fontSize": "16px"},
                    ),
                    html.Span(
                        "Return, volatility, and cost bubbles react instantly.",
                        style=muted_text(theme) | {"fontSize": "13px"},
                    ),
                ],
                style={"display": "flex", "flexDirection": "column", "gap": "2px"},
            ),
            dcc.Graph(
                id="hero-comparison-chart",
                config={"displayModeBar": False},
                style={"height": "320px"},
            ),
            html.Div(id="hero-comparison-chart-metadata"),
        ],
    )
    advanced_toggles = html.Details(
        className="mobile-disclosure hero-disclosure",
        children=[
            html.Summary("Advanced hero controls"),
            html.Div([quick_toggles], className="mobile-disclosure-content"),
        ],
    )
    return hero_banner(
        title="Decide faster with evidence-backed, cost-aware rules",
        subtitle="Use KPI, Strategy Lab, and Compare signals to confirm what is robust before you deploy.",
        thesis="Confirm trend participation first, stress-test sensitivity second, and only scale when tradeoffs stay favorable under higher drag.",
        kpis=hero_kpis,
        actions=[
            button_link(
                "Confirm signal",
                href="#strategy-tab",
                theme_key=theme_key,
                primary=True,
            ),
            button_link(
                "Run stress test",
                href="#comparison-tab",
                theme_key=theme_key,
                primary=False,
            ),
            button_link(
                "Run discipline check",
                href="#cost-slider",
                theme_key=theme_key,
                primary=False,
            ),
        ],
        theme_key=theme_key,
        hero_visual=hero_visual,
        quick_toggles=[advanced_toggles],
    )


def _scenario_panel(theme_key: str) -> html.Div:
    theme = get_theme(theme_key)
    scenario_options = [
        {
            "label": html.Div(
                className="scenario-option",
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "6px",
                    "padding": "10px 12px",
                    "borderRadius": "12px",
                    "border": f"1px solid {theme['grid']}",
                    "background": f"rgba(148, 163, 184, {0.12 if theme['mode']=='light' else 0.22})",
                },
                children=[
                    html.Div(
                        preset["title"],
                        style={"fontWeight": 700, "fontSize": "15px"},
                    ),
                    html.Span(
                        preset["description"],
                        style=muted_text(theme) | {"fontSize": "13px"},
                    ),
                    html.Div(
                        [
                            html.Span(f"Ticker: {preset['ticker']}"),
                            html.Span(f"Window: {preset['window']}d"),
                            html.Span(f"Cost drag: {preset['cost_bps']} bps"),
                            html.Span(f"Horizon: {preset['horizon']}d"),
                        ],
                        style={
                            "display": "flex",
                            "flexWrap": "wrap",
                            "gap": "8px",
                            "fontSize": "12px",
                            "color": theme["muted_text"],
                        },
                    ),
                ],
            ),
            "value": key,
        }
        for key, preset in SCENARIO_PRESETS.items()
    ]
    action_box_style = {
        "display": "flex",
        "flexDirection": "column",
        "gap": "10px",
        "padding": "12px",
        "borderRadius": "12px",
        "border": f"1px solid {theme['grid']}",
        "background": f"rgba(15,23,42,{0.05 if theme['mode']=='light' else 0.3})",
    }
    primary_button_style = {
        "padding": "10px 14px",
        "borderRadius": "10px",
        "border": f"1px solid {theme['accent']}",
        "background": theme["accent"],
        "color": "#0b1224" if theme["mode"] == "light" else "#0f172a",
        "fontWeight": 700,
        "cursor": "pointer",
    }
    ghost_button_style = {
        "padding": "10px 14px",
        "borderRadius": "10px",
        "border": f"1px solid {theme['grid']}",
        "background": "transparent",
        "color": theme["text"],
        "fontWeight": 600,
        "cursor": "pointer",
    }
    return html.Div(
        className="scenario-panel",
        children=[
            html.Div(
                children=[
                    html.Div(
                        [
                            html.Div(
                                "Stress-test a scenario", style={"fontWeight": 700}
                            ),
                            html.Span(
                                "Pick a preset to load assumptions quickly, then validate sensitivity across views.",
                                style=muted_text(theme),
                            ),
                        ]
                    ),
                    dcc.RadioItems(
                        id="scenario-selector",
                        options=scenario_options,
                        value=next(iter(SCENARIO_PRESETS.keys())),
                        inputStyle={"marginRight": "10px", "marginLeft": "2px"},
                        labelStyle={
                            "display": "block",
                            "marginBottom": "10px",
                            "cursor": "pointer",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "10px",
                },
            ),
            html.Div(
                style=action_box_style,
                className="scenario-actions",
                children=[
                    html.Div(
                        [
                            html.Span("Scenario controls", style={"fontWeight": 700}),
                            html.Span(
                                "Load a preset to update ticker, horizon, costs, and hero quick toggles in one pass.",
                                style=muted_text(theme) | {"fontSize": "13px"},
                            ),
                        ],
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            "gap": "4px",
                        },
                    ),
                    html.Button(
                        "Load stress-test preset",
                        id="scenario-apply",
                        n_clicks=0,
                        style=primary_button_style,
                    ),
                    html.Button(
                        "Recompute stress test",
                        id="scenario-rerun",
                        n_clicks=0,
                        style=ghost_button_style,
                    ),
                    html.Span(
                        "Tip: recompute after manual edits to keep all views synchronized.",
                        style=muted_text(theme) | {"fontSize": "12px"},
                    ),
                ],
            ),
        ],
    )


def _signal_confirmation_section(theme_key: str) -> html.Div:
    theme = get_theme(theme_key)
    summary_cards = [
        surface_card(
            theme_key=theme_key,
            title=item["title"],
            children=[
                html.Div(
                    item["headline"], style={"fontSize": "18px", "fontWeight": 600}
                ),
                html.P(item["detail"], style=muted_text(theme)),
            ],
        )
        for item in STRATEGY_SUMMARIES
    ]
    return section_block(
        title="1. Signal confirmation",
        description="Confirm trend context first, then compare signal behavior before changing execution assumptions.",
        theme_key=theme_key,
        eyebrow_text="Workflow step",
        content=html.Div(
            style={"display": "flex", "flexDirection": "column", "gap": "16px"},
            children=[
                html.Div(
                    className="control-bar",
                    children=[
                        html.Div(
                            className="control-card",
                            children=[
                                html.Label(
                                    "Ticker",
                                    htmlFor="ticker-dropdown",
                                    **{"aria-label": "Ticker selector"},
                                ),
                                dcc.Dropdown(
                                    id="ticker-dropdown",
                                    options=[
                                        {"label": t, "value": t}
                                        for t in _SAMPLE.tickers
                                    ],
                                    value=_SAMPLE.tickers[0],
                                    clearable=False,
                                ),
                            ],
                        ),
                        html.Details(
                            className="mobile-disclosure control-disclosure",
                            children=[
                                html.Summary("Advanced controls"),
                                html.Div(
                                    className="mobile-disclosure-content",
                                    children=[
                                        html.Div(
                                            className="control-card",
                                            children=[
                                                html.Label(
                                                    "Lookback window (days)",
                                                    htmlFor="window-slider",
                                                    **{
                                                        "aria-label": "Lookback window slider"
                                                    },
                                                ),
                                                dcc.Slider(
                                                    id="window-slider",
                                                    min=30,
                                                    max=180,
                                                    step=10,
                                                    value=90,
                                                    marks={
                                                        30: "30",
                                                        90: "90",
                                                        180: "180",
                                                    },
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    className="decision-chart-grid",
                    children=[
                        surface_card(
                            theme_key=theme_key,
                            class_name="decision-chart-card",
                            title="Market replay",
                            subtitle="Read the trend context before acting.",
                            children=[
                                html.P(
                                    "Use ticker and lookback inputs to confirm where the current move sits in context.",
                                    style=muted_text(theme),
                                ),
                                _graph_container(
                                    "price-spotlight",
                                    "Market replay spotlight chart",
                                    "360px",
                                ),
                                chart_narrative_block(
                                    narrative=ChartNarrative("", "", ""),
                                    theme_key=theme_key,
                                    component_id="price-spotlight-narrative",
                                ),
                            ],
                        ),
                        surface_card(
                            theme_key=theme_key,
                            class_name="supporting-chart-card",
                            title="Signals vs. benchmark",
                            subtitle="Validate signal behavior against buy-and-hold.",
                            children=[
                                html.P(
                                    "Check whether rules stay invested during constructive trends before tuning anything else.",
                                    style=muted_text(theme),
                                ),
                                _graph_container(
                                    "strategy-spotlight",
                                    "Strategy spotlight chart",
                                    "280px",
                                ),
                                chart_narrative_block(
                                    narrative=ChartNarrative("", "", ""),
                                    theme_key=theme_key,
                                    component_id="strategy-spotlight-narrative",
                                ),
                            ],
                        ),
                    ],
                ),
                responsive_grid(summary_cards, min_width="260px"),
            ],
        ),
    )


def _scenario_stress_test_section(theme_key: str) -> html.Div:
    theme = get_theme(theme_key)
    steps = [
        surface_card(
            theme_key=theme_key,
            title=step["title"],
            children=[html.P(step["body"], style=muted_text(theme))],
        )
        for step in WORKFLOW_STEPS
    ]
    return section_block(
        title="2. Scenario stress-test",
        description="Apply scenario presets, then pressure-test outcomes with comparison and timeline views.",
        theme_key=theme_key,
        eyebrow_text="Workflow step",
        content=html.Div(
            style={"display": "flex", "flexDirection": "column", "gap": "16px"},
            children=[
                _scenario_panel(theme_key),
                html.Div(
                    className="control-bar",
                    children=[
                        html.Details(
                            className="mobile-disclosure control-disclosure",
                            children=[
                                html.Summary("Advanced controls"),
                                html.Div(
                                    className="mobile-disclosure-content",
                                    children=[
                                        html.Div(
                                            className="control-card",
                                            children=[
                                                html.Label(
                                                    "Timeline horizon",
                                                    htmlFor="horizon-dropdown",
                                                    **{
                                                        "aria-label": "Timeline horizon selector"
                                                    },
                                                ),
                                                dcc.Dropdown(
                                                    id="horizon-dropdown",
                                                    options=[
                                                        {
                                                            "label": "3 months",
                                                            "value": 60,
                                                        },
                                                        {
                                                            "label": "6 months",
                                                            "value": 120,
                                                        },
                                                        {
                                                            "label": "12 months",
                                                            "value": 252,
                                                        },
                                                    ],
                                                    value=120,
                                                    clearable=False,
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    className="decision-chart-grid",
                    children=[
                        surface_card(
                            theme_key=theme_key,
                            class_name="decision-chart-card",
                            title="Comparison matrix",
                            subtitle="Spot return, volatility, and cost trade-offs fast.",
                            children=[
                                _graph_container(
                                    "matrix-spotlight",
                                    "Comparison matrix spotlight chart",
                                    "380px",
                                ),
                                chart_narrative_block(
                                    narrative=ChartNarrative("", "", ""),
                                    theme_key=theme_key,
                                    component_id="matrix-spotlight-narrative",
                                ),
                            ],
                        ),
                        surface_card(
                            theme_key=theme_key,
                            class_name="supporting-chart-card",
                            title="Timeline overlays",
                            subtitle="Check if the rule held through regime shifts.",
                            children=[
                                _graph_container(
                                    "timeline-spotlight",
                                    "Timeline overlay spotlight chart",
                                    "300px",
                                ),
                                chart_narrative_block(
                                    narrative=ChartNarrative("", "", ""),
                                    theme_key=theme_key,
                                    component_id="timeline-spotlight-narrative",
                                ),
                            ],
                        ),
                    ],
                ),
                responsive_grid(steps, min_width="240px"),
            ],
        ),
    )


def _discipline_check_section(theme_key: str) -> html.Div:
    theme = get_theme(theme_key)
    cards = [
        surface_card(
            theme_key=theme_key,
            title=sim["name"],
            children=[
                html.Div(sim["result"], style={"fontWeight": 600}),
                html.P(sim["note"], style=muted_text(theme)),
            ],
        )
        for sim in SIMULATION_FEED
    ]
    return section_block(
        title="3. Entry/exit discipline check",
        description="Model cost drag and review simulation outcomes before deciding to trade less or stay invested.",
        theme_key=theme_key,
        eyebrow_text="Workflow step",
        content=html.Div(
            style={"display": "flex", "flexDirection": "column", "gap": "16px"},
            children=[
                html.Div(
                    className="control-bar",
                    children=[
                        html.Details(
                            className="mobile-disclosure control-disclosure",
                            children=[
                                html.Summary("Advanced controls"),
                                html.Div(
                                    className="mobile-disclosure-content",
                                    children=[
                                        html.Div(
                                            className="control-card",
                                            children=[
                                                html.Label(
                                                    "Cost drag (bps)",
                                                    htmlFor="cost-slider",
                                                    **{
                                                        "aria-label": "Cost drag slider"
                                                    },
                                                ),
                                                dcc.Slider(
                                                    id="cost-slider",
                                                    min=0,
                                                    max=100,
                                                    step=5,
                                                    value=25,
                                                    marks={
                                                        0: "0",
                                                        50: "50",
                                                        100: "100",
                                                    },
                                                    tooltip={"placement": "bottom"},
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    className="decision-chart-grid",
                    children=[
                        surface_card(
                            theme_key=theme_key,
                            class_name="decision-chart-card",
                            title="Execution costs",
                            subtitle="Stress entry/exit assumptions before scaling.",
                            children=[
                                _graph_container(
                                    "cost-spotlight",
                                    "Execution cost spotlight chart",
                                    "340px",
                                ),
                                chart_narrative_block(
                                    narrative=ChartNarrative("", "", ""),
                                    theme_key=theme_key,
                                    component_id="cost-spotlight-narrative",
                                ),
                            ],
                        ),
                    ],
                ),
                responsive_grid(cards, min_width="260px"),
            ],
        ),
    )


def _workflow_sections(theme_key: str) -> html.Div:
    return text_stack(
        [
            _signal_confirmation_section(theme_key),
            _scenario_stress_test_section(theme_key),
            _discipline_check_section(theme_key),
        ],
        gap="20px",
    )


def _strategy_tab(theme_key: str) -> html.Div:
    return html.Div(
        className="tab-grid tab-grid--two",
        children=[
            _build_card(
                "Strategy Comparison",
                [
                    _graph_container(
                        "strategy-chart-secondary",
                        "Secondary strategy comparison chart",
                        "400px",
                    ),
                    html.P("Signals derived from interactive moving-average helpers."),
                ],
                theme_key,
            ),
            _build_card(
                "Execution Context",
                [
                    _graph_container(
                        "cost-impact-chart-secondary",
                        "Secondary cost impact chart",
                        "400px",
                    ),
                ],
                theme_key,
            ),
        ],
    )


def _cost_tab(theme_key: str) -> html.Div:
    return html.Div(
        children=[
            _build_card(
                "Cost & Impact Analysis",
                [
                    _graph_container(
                        "cost-impact-chart", "Cost and impact analysis chart", "400px"
                    ),
                    html.P("Liquidity scaled against estimated execution slippage."),
                ],
                theme_key,
            ),
        ]
    )


def _time_in_market_tab(theme_key: str) -> html.Div:
    return html.Div(
        className="tab-grid tab-grid--two",
        children=[
            _build_card(
                "Time in Market Exposure",
                [
                    _graph_container(
                        "time-in-market-chart", "Time in market pie chart", "360px"
                    ),
                    html.P("Estimate of time spent participating in positive trends."),
                ],
                theme_key,
            ),
            _build_card(
                "Price Context",
                [
                    _graph_container(
                        "price-chart-secondary", "Secondary price chart", "360px"
                    )
                ],
                theme_key,
            ),
        ],
    )


def _comparison_tab(theme_key: str) -> html.Div:
    tips = guidance_tooltips()
    return html.Div(
        className="tab-grid tab-grid--comparison",
        children=[
            _build_card(
                "Return / Volatility / Cost Matrix",
                [
                    _graph_container(
                        "comparison-matrix",
                        "Return volatility and cost matrix",
                        "420px",
                    ),
                    html.Div(
                        tips,
                        style={"display": "flex", "gap": "12px", "flexWrap": "wrap"},
                    ),
                ],
                theme_key,
            ),
            _build_card(
                "Timeline Overlay",
                [
                    _graph_container(
                        "timeline-overlay", "Timeline overlay chart", "420px"
                    ),
                    myth_busting_callouts(),
                ],
                theme_key,
            ),
        ],
    )


def _diagnostics_tab(theme_key: str) -> html.Div:
    return html.Div(
        children=[
            _build_card(
                "Data Diagnostics",
                [
                    _graph_container(
                        "diagnostics-chart", "Diagnostics histogram", "400px"
                    ),
                    html.P("Distribution of daily returns for sanity checks."),
                ],
                theme_key,
            ),
        ]
    )


def build_app() -> Dash:
    app = Dash(
        __name__, title="python-stocks dashboard", suppress_callback_exceptions=True
    )

    app.layout = html.Div(
        id="page-root",
        style=page_style(get_theme(DEFAULT_THEME_KEY)),
        **{"data-theme": DEFAULT_THEME_KEY},
        children=[
            html.Main(
                className="page-shell",
                children=[
                    page_header(
                        title="Build resilient, cost-aware equity rules",
                        subtitle="Decide, confirm, and stress-test with the Strategy Lab workflow",
                        theme_key=DEFAULT_THEME_KEY,
                        controls=[
                            html.Div(
                                [
                                    html.Label(
                                        "Theme",
                                        htmlFor="theme-toggle",
                                        style={"marginRight": "8px"},
                                    ),
                                    dcc.RadioItems(
                                        id="theme-toggle",
                                        options=[
                                            {"label": "Light", "value": "light"},
                                            {"label": "Dark", "value": "dark"},
                                        ],
                                        value=DEFAULT_THEME_KEY,
                                        inline=True,
                                    ),
                                ],
                                style={
                                    "display": "flex",
                                    "alignItems": "center",
                                    "gap": "4px",
                                    "padding": "10px 12px",
                                    "borderRadius": "12px",
                                    "background": "rgba(148, 163, 184, 0.12)",
                                },
                                role="group",
                                **{"aria-label": "Theme selector"},
                            )
                        ],
                    ),
                    _kpi_hero(DEFAULT_THEME_KEY),
                    surface_card(
                        theme_key=DEFAULT_THEME_KEY,
                        title="Run a decision workflow without losing market exposure context",
                        subtitle="Use realistic inputs so matrix and overlay reactions reflect confidence, sensitivity, and tradeoff shifts.",
                        children=[
                            html.Div(className="section-divider"),
                            html.P(
                                "Use the workflow blocks below to confirm signals, stress-test scenarios, and verify cost discipline in sequence.",
                            ),
                        ],
                    ),
                    _workflow_sections(DEFAULT_THEME_KEY),
                    dcc.Tabs(
                        id="dashboard-tabs",
                        value="overview",
                        children=[
                            dcc.Tab(
                                id="overview-tab",
                                label="Overview",
                                value="overview",
                                children=[_overview_tab(DEFAULT_THEME_KEY)],
                            ),
                            dcc.Tab(
                                id="strategy-tab",
                                label="Strategy Lab",
                                value="strategy",
                                children=[_strategy_tab(DEFAULT_THEME_KEY)],
                            ),
                            dcc.Tab(
                                id="cost-tab",
                                label="Cost/Impact Analysis",
                                value="cost",
                                children=[_cost_tab(DEFAULT_THEME_KEY)],
                            ),
                            dcc.Tab(
                                id="comparison-tab",
                                label="Comparisons",
                                value="comparisons",
                                children=[_comparison_tab(DEFAULT_THEME_KEY)],
                            ),
                            dcc.Tab(
                                id="time-tab",
                                label="Time in Market",
                                value="timelesson",
                                children=[_time_in_market_tab(DEFAULT_THEME_KEY)],
                            ),
                            dcc.Tab(
                                id="diagnostics-tab",
                                label="Data Diagnostics",
                                value="diagnostics",
                                children=[_diagnostics_tab(DEFAULT_THEME_KEY)],
                            ),
                        ],
                    ),
                ],
            )
        ],
    )

    @app.callback(
        Output("ticker-dropdown", "value"),
        Output("window-slider", "value"),
        Output("cost-slider", "value"),
        Output("horizon-dropdown", "value"),
        Output("hero-preset-toggle", "value"),
        Output("hero-ticker-toggle", "value"),
        Input("scenario-apply", "n_clicks"),
        State("scenario-selector", "value"),
        prevent_initial_call=True,
    )
    def _apply_scenario_preset(
        n_clicks: int | None, scenario_key: str | None
    ):  # pragma: no cover - UI glue
        if not n_clicks or not scenario_key:
            return (
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        preset = SCENARIO_PRESETS.get(scenario_key)
        if not preset:
            return (
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
            )
        return (
            preset["ticker"],
            preset["window"],
            preset["cost_bps"],
            preset["horizon"],
            preset["hero_preset"],
            preset["ticker"],
        )

    @app.callback(
        Output("page-root", "style"),
        Output("page-root", "data-theme"),
        Output("hero-comparison-chart", "figure"),
        Output("price-chart", "figure"),
        Output("strategy-chart", "figure"),
        Output("cost-impact-chart", "figure"),
        Output("time-in-market-chart", "figure"),
        Output("diagnostics-chart", "figure"),
        Output("price-chart-secondary", "figure"),
        Output("strategy-chart-secondary", "figure"),
        Output("cost-impact-chart-secondary", "figure"),
        Output("comparison-matrix", "figure"),
        Output("timeline-overlay", "figure"),
        Output("price-spotlight", "figure"),
        Output("strategy-spotlight", "figure"),
        Output("cost-spotlight", "figure"),
        Output("matrix-spotlight", "figure"),
        Output("timeline-spotlight", "figure"),
        Output("price-spotlight-narrative", "children"),
        Output("strategy-spotlight-narrative", "children"),
        Output("cost-spotlight-narrative", "children"),
        Output("matrix-spotlight-narrative", "children"),
        Output("timeline-spotlight-narrative", "children"),
        *[Output(f"{chart_id}-metadata", "children") for chart_id in _CHART_IDS],
        Input("ticker-dropdown", "value"),
        Input("theme-toggle", "value"),
        Input("window-slider", "value"),
        Input("cost-slider", "value"),
        Input("horizon-dropdown", "value"),
        Input("hero-ticker-toggle", "value"),
        Input("hero-preset-toggle", "value"),
        Input("scenario-rerun", "n_clicks"),
    )
    def _update_charts(
        ticker: str,
        theme_key: str,
        window: int,
        cost_bps: int,
        horizon: int,
        hero_ticker: str,
        hero_preset: str,
        scenario_rerun_clicks: int | None,
    ):
        theme = get_theme(theme_key)
        cost_penalty = (cost_bps or 0) / 10_000
        window = window or 60
        horizon = horizon or 120
        hero_config = _HERO_PRESETS.get(hero_preset, _HERO_PRESETS["balanced"])
        hero_cost_penalty = hero_config["cost_bps"] / 10_000
        hero_window = hero_config["window"]
        price_chart = price_trend_figure(_SAMPLE, ticker, theme)
        strategy_chart = strategy_signal_figure(_SAMPLE, ticker, theme)
        cost_chart = cost_impact_figure(_SAMPLE, ticker, theme)
        time_chart = time_in_market_figure(_SAMPLE, ticker, theme)
        diagnostics_chart = diagnostics_figure(_SAMPLE, ticker, theme)
        comparison_chart = comparison_matrix_figure(
            _SAMPLE, ticker, theme, window=window, cost_penalty=cost_penalty
        )
        timeline_chart = timeline_overlay_figure(
            _SAMPLE, ticker, theme, horizon=horizon
        )
        hero_chart = comparison_matrix_figure(
            _SAMPLE,
            hero_ticker or ticker,
            theme,
            window=hero_window,
            cost_penalty=hero_cost_penalty,
        )
        revision_tag = (
            f"{ticker}-{window}-{cost_bps}-{horizon}-{hero_ticker}-{hero_preset}-"
            f"{scenario_rerun_clicks or 0}"
        )
        for fig in [
            hero_chart,
            price_chart,
            strategy_chart,
            cost_chart,
            time_chart,
            diagnostics_chart,
            comparison_chart,
            timeline_chart,
        ]:
            fig.update_layout(uirevision=revision_tag)
        metadata = _build_chart_metadata(
            theme_key=theme_key,
            ticker=ticker,
            window=window,
            cost_bps=cost_bps,
            horizon=horizon,
            hero_ticker=hero_ticker or ticker,
            hero_preset=hero_preset,
            sample=_SAMPLE,
        )
        narratives = {}
        close_series = _SAMPLE.history[ticker]["Close"].sort_index()
        volume_series = _SAMPLE.history[ticker]["Volume"].sort_index()
        for spotlight_id, label in SPOTLIGHT_LABELS.items():
            narratives[spotlight_id] = chart_narrative_block(
                narrative=build_market_narrative(
                    close_series,
                    volume_series,
                    cost_bps=cost_bps or 0,
                    label=label,
                ),
                theme_key=theme_key,
            )
        return (
            page_style(theme),
            theme_key,
            hero_chart,
            price_chart,
            strategy_chart,
            cost_chart,
            time_chart,
            diagnostics_chart,
            price_chart,
            strategy_chart,
            cost_chart,
            comparison_chart,
            timeline_chart,
            price_chart,
            strategy_chart,
            cost_chart,
            comparison_chart,
            timeline_chart,
            narratives["price-spotlight"],
            narratives["strategy-spotlight"],
            narratives["cost-spotlight"],
            narratives["matrix-spotlight"],
            narratives["timeline-spotlight"],
            *[metadata[f"{chart_id}-metadata"] for chart_id in _CHART_IDS],
        )

    return app


app = build_app()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
