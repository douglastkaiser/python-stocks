"""Dash dashboard entrypoint for python-stocks."""

from __future__ import annotations

from typing import List

from dash import Dash, Input, Output, dcc, html

from python_stocks.dashboard.components import (
    MarketSample,
    comparison_matrix_figure,
    cost_impact_figure,
    diagnostics_figure,
    guidance_tooltips,
    myth_busting_callouts,
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


def _build_card(
    title: str, body: List[html.Div | dcc.Graph], theme_key: str
) -> html.Div:
    theme = get_theme(theme_key)
    return html.Div(
        style=surface_style(theme),
        children=[
            html.H3(title, style={"marginTop": 0, "marginBottom": "12px"}),
            *body,
        ],
    )


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
        children=[
            html.Header(
                style={
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "space-between",
                    "marginBottom": "16px",
                },
                children=[
                    html.Div(
                        [
                            html.H1("Python Stocks Dashboard", style={"margin": 0}),
                            html.P(
                                "Interactive exploration built on Plotly + Dash",
                                style={
                                    "margin": 0,
                                    "color": get_theme(DEFAULT_THEME_KEY)["muted_text"],
                                },
                            ),
                        ]
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
                        style={"display": "flex", "alignItems": "center", "gap": "4px"},
                        role="group",
                        **{"aria-label": "Theme selector"},
                    ),
                ],
            ),
            html.Div(
                style={"display": "flex", "gap": "12px", "marginBottom": "12px"},
                children=[
                    html.Div(
                        [
                            html.Label(
                                "Ticker",
                                htmlFor="ticker-dropdown",
                                **{"aria-label": "Ticker selector"},
                            ),
                            dcc.Dropdown(
                                id="ticker-dropdown",
                                options=[
                                    {"label": t, "value": t} for t in _SAMPLE.tickers
                                ],
                                value=_SAMPLE.tickers[0],
                                clearable=False,
                                style={"minWidth": "180px"},
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Label(
                                "Lookback window (days)",
                                htmlFor="window-slider",
                                **{"aria-label": "Lookback window slider"},
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
                        style={"minWidth": "220px"},
                    ),
                    html.Div(
                        [
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
                        style={"minWidth": "220px"},
                    ),
                    html.Div(
                        [
                            html.Label(
                                "Timeline horizon",
                                htmlFor="horizon-dropdown",
                                **{"aria-label": "Timeline horizon selector"},
                            ),
                            dcc.Dropdown(
                                id="horizon-dropdown",
                                options=[
                                    {"label": "3 months", "value": 60},
                                    {"label": "6 months", "value": 120},
                                    {"label": "12 months", "value": 252},
                                ],
                                value=120,
                                clearable=False,
                                style={"minWidth": "160px"},
                            ),
                        ],
                    ),
                ],
            ),
            dcc.Tabs(
                id="dashboard-tabs",
                value="overview",
                children=[
                    dcc.Tab(
                        label="Overview",
                        value="overview",
                        children=[_overview_tab(DEFAULT_THEME_KEY)],
                    ),
                    dcc.Tab(
                        label="Strategy Lab",
                        value="strategy",
                        children=[_strategy_tab(DEFAULT_THEME_KEY)],
                    ),
                    dcc.Tab(
                        label="Cost/Impact Analysis",
                        value="cost",
                        children=[_cost_tab(DEFAULT_THEME_KEY)],
                    ),
                    dcc.Tab(
                        label="Comparisons",
                        value="comparisons",
                        children=[_comparison_tab(DEFAULT_THEME_KEY)],
                    ),
                    dcc.Tab(
                        label="Time in Market",
                        value="timelesson",
                        children=[_time_in_market_tab(DEFAULT_THEME_KEY)],
                    ),
                    dcc.Tab(
                        label="Data Diagnostics",
                        value="diagnostics",
                        children=[_diagnostics_tab(DEFAULT_THEME_KEY)],
                    ),
                ],
            ),
        ],
    )

    @app.callback(
        Output("page-root", "style"),
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
        return (
            page_style(theme),
            price_trend_figure(_SAMPLE, ticker, theme),
            strategy_signal_figure(_SAMPLE, ticker, theme),
            cost_impact_figure(_SAMPLE, ticker, theme),
            time_in_market_figure(_SAMPLE, ticker, theme),
            diagnostics_figure(_SAMPLE, ticker, theme),
            price_trend_figure(_SAMPLE, ticker, theme),
            strategy_signal_figure(_SAMPLE, ticker, theme),
            cost_impact_figure(_SAMPLE, ticker, theme),
            comparison_matrix_figure(
                _SAMPLE, ticker, theme, window=window, cost_penalty=cost_penalty
            ),
            timeline_overlay_figure(_SAMPLE, ticker, theme, horizon=horizon),
        )

    return app


app = build_app()


if __name__ == "__main__":
    app.run_server(debug=True)
