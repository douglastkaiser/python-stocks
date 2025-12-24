"""Dash dashboard entrypoint for python-stocks."""

from __future__ import annotations

from typing import List

from dash import Dash, Input, Output, dcc, html

from python_stocks.dashboard.components import (
    MarketSample,
    button_link,
    comparison_matrix_figure,
    cost_impact_figure,
    diagnostics_figure,
    guidance_tooltips,
    hero_banner,
    kpi_stat,
    myth_busting_callouts,
    muted_text,
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
)


_SAMPLE = MarketSample.demo(["AAPL", "MSFT", "SPY", "QQQ"])
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
LEARNING_STEPS = [
    {
        "title": "Start with price context",
        "body": "Replay recent swings to see how signals react before real capital is at risk.",
    },
    {
        "title": "Layer in costs",
        "body": "Model slippage and fees so ideas survive outside of notebooks.",
    },
    {
        "title": "Compare outcomes",
        "body": "Use the comparison matrix to pressure test edge, drawdowns, and capacity.",
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
SHOWCASE_FEATURES = [
    {
        "title": "Market replay",
        "subtitle": "Moving-average overlays make price context easier to read.",
        "body": "Use the horizon control to zoom into recent swings and see how trends persisted.",
        "graph_id": "price-spotlight",
        "label": "Market replay spotlight chart",
        "height": "280px",
    },
    {
        "title": "Signals vs. benchmark",
        "subtitle": "Equity curves update live as you tweak the lookback window.",
        "body": "Watch strategy equity alongside buy-and-hold to quickly see where rules diverge.",
        "graph_id": "strategy-spotlight",
        "label": "Strategy spotlight chart",
        "height": "280px",
    },
    {
        "title": "Execution costs",
        "subtitle": "Costs and liquidity are front-and-center instead of buried in tooltips.",
        "body": "Dial in slippage assumptions to preview how rebalance churn changes the story.",
        "graph_id": "cost-spotlight",
        "label": "Execution cost spotlight chart",
        "height": "280px",
    },
    {
        "title": "Comparison matrix",
        "subtitle": "Return, volatility, and cost reactions in one view.",
        "body": "The matrix reacts instantly so you can iterate on inputs without losing the plot.",
        "graph_id": "matrix-spotlight",
        "label": "Comparison matrix spotlight chart",
        "height": "300px",
    },
    {
        "title": "Timeline overlays",
        "subtitle": "Contextualize signals against events and market phases.",
        "body": "Overlay momentum windows on the timeline to explain why a rule stayed invested.",
        "graph_id": "timeline-spotlight",
        "label": "Timeline overlay spotlight chart",
        "height": "300px",
    },
]


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
            )
        ],
    )


def _overview_tab(theme_key: str) -> html.Div:
    return html.Div(
        className="grid",
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
        style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px"},
    )


def _kpi_hero(theme_key: str) -> html.Div:
    hero_kpis = [
        kpi_stat(
            label="Benchmark discipline",
            value="92% time invested",
            caption="Momentum rules stick with the market instead of timing it.",
            theme_key=theme_key,
        ),
        kpi_stat(
            label="Drag minimized",
            value="< 40 bps modeled",
            caption="Execution guardrails keep most signals tradable.",
            theme_key=theme_key,
        ),
        kpi_stat(
            label="Replay speed",
            value="< 1s refresh",
            caption="Adjust sliders and see the comparison matrix update instantly.",
            theme_key=theme_key,
        ),
    ]
    return hero_banner(
        title="Build rules that match the market before you try to beat it",
        subtitle="Strategy lab + comparison tools help you pressure test signals, costs, and capacity with live feedback.",
        thesis="Edge comes from disciplined execution: stay invested, size responsibly, and avoid churn that erodes returns.",
        kpis=hero_kpis,
        actions=[
            button_link(
                "Open Strategy Lab",
                href="#strategy-tab",
                theme_key=theme_key,
                primary=True,
            ),
            button_link(
                "Jump to Comparisons",
                href="#comparison-tab",
                theme_key=theme_key,
                primary=False,
            ),
        ],
        theme_key=theme_key,
    )


def _strategies_at_a_glance(theme_key: str) -> html.Div:
    theme = get_theme(theme_key)
    cards = [
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
        title="Strategies at a glance",
        description="Snapshots from the Strategy Lab show how cost-aware rules behave before you deploy capital.",
        theme_key=theme_key,
        content=responsive_grid(cards, min_width="260px"),
    )


def _learning_path(theme_key: str) -> html.Div:
    theme = get_theme(theme_key)
    steps = [
        surface_card(
            theme_key=theme_key,
            title=step["title"],
            children=[html.P(step["body"], style=muted_text(theme))],
        )
        for step in LEARNING_STEPS
    ]
    return section_block(
        title="Learning path",
        description="A guided sequence keeps you focused: explore, price in costs, then compare outcomes.",
        theme_key=theme_key,
        content=responsive_grid(steps, min_width="240px"),
    )


def _latest_simulations(theme_key: str) -> html.Div:
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
        title="Latest simulations",
        description="Server-side runs summarize how tweaks to rules and costs ripple through results.",
        theme_key=theme_key,
        content=responsive_grid(cards, min_width="260px"),
    )


def _guided_showcase(theme_key: str) -> html.Div:
    theme = get_theme(theme_key)
    cards = [
        surface_card(
            theme_key=theme_key,
            title=feature["title"],
            subtitle=feature["subtitle"],
            children=[
                html.P(feature["body"], style=muted_text(theme)),
                _graph_container(
                    feature["graph_id"], feature["label"], feature["height"]
                ),
            ],
        )
        for feature in SHOWCASE_FEATURES
    ]
    return section_block(
        title="Guided dashboards and strategy explainers",
        description="Front-page snapshots highlight the visuals you care about while controls stay within reach.",
        theme_key=theme_key,
        content=responsive_grid(cards, min_width="260px", gap="16px"),
    )


def _strategy_tab(theme_key: str) -> html.Div:
    return html.Div(
        className="grid",
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
        style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px"},
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
        style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px"},
        children=[
            _build_card(
                "Time in Market Lesson",
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
        style={"display": "grid", "gridTemplateColumns": "2fr 1fr", "gap": "16px"},
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
                    html.Div(
                        style={
                            "display": "flex",
                            "justifyContent": "space-between",
                            "alignItems": "center",
                            "gap": "12px",
                            "flexWrap": "wrap",
                        },
                        children=[
                            text_stack(
                                [
                                    html.Div(
                                        "Preview the Strategy Lab dashboard",
                                        style={
                                            "fontSize": "14px",
                                            "color": "#64748b",
                                            "fontWeight": 600,
                                        },
                                    ),
                                    html.H1(
                                        "Build resilient, cost-aware equity rules",
                                        style={"margin": 0},
                                    ),
                                ],
                                gap="4px",
                            ),
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
                            ),
                        ],
                    ),
                    _kpi_hero(DEFAULT_THEME_KEY),
                    surface_card(
                        theme_key=DEFAULT_THEME_KEY,
                        title="Tune a strategy without losing market exposure",
                        subtitle="Use realistic inputs so the comparison matrix and overlays react like a real account would.",
                        children=[
                            html.Div(className="section-divider"),
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
                                                marks={30: "30", 90: "90", 180: "180"},
                                            ),
                                        ],
                                        style={"minWidth": "240px"},
                                    ),
                                    html.Div(
                                        className="control-card",
                                        children=[
                                            html.Label(
                                                "Cost drag (bps)",
                                                htmlFor="cost-slider",
                                                **{"aria-label": "Cost drag slider"},
                                            ),
                                            dcc.Slider(
                                                id="cost-slider",
                                                min=0,
                                                max=100,
                                                step=5,
                                                value=25,
                                                marks={0: "0", 50: "50", 100: "100"},
                                                tooltip={"placement": "bottom"},
                                            ),
                                        ],
                                        style={"minWidth": "240px"},
                                    ),
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
                                                    {"label": "3 months", "value": 60},
                                                    {"label": "6 months", "value": 120},
                                                    {
                                                        "label": "12 months",
                                                        "value": 252,
                                                    },
                                                ],
                                                value=120,
                                                clearable=False,
                                            ),
                                        ],
                                        style={"minWidth": "200px"},
                                    ),
                                ],
                            ),
                        ],
                    ),
                    _guided_showcase(DEFAULT_THEME_KEY),
                    text_stack(
                        [
                            _strategies_at_a_glance(DEFAULT_THEME_KEY),
                            _learning_path(DEFAULT_THEME_KEY),
                            _latest_simulations(DEFAULT_THEME_KEY),
                        ],
                        gap="20px",
                    ),
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
        Output("page-root", "style"),
        Output("page-root", "data-theme"),
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
        Input("ticker-dropdown", "value"),
        Input("theme-toggle", "value"),
        Input("window-slider", "value"),
        Input("cost-slider", "value"),
        Input("horizon-dropdown", "value"),
    )
    def _update_charts(
        ticker: str, theme_key: str, window: int, cost_bps: int, horizon: int
    ):
        theme = get_theme(theme_key)
        cost_penalty = (cost_bps or 0) / 10_000
        window = window or 60
        horizon = horizon or 120
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
        return (
            page_style(theme),
            theme_key,
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
        )

    return app


app = build_app()


if __name__ == "__main__":
    app.run_server(debug=True)
