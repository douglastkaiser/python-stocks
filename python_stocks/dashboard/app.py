"""Dash dashboard entrypoint for python-stocks."""
from __future__ import annotations

from typing import List

from dash import Dash, Input, Output, dcc, html

from python_stocks.dashboard.components import (
    MarketSample,
    cost_impact_figure,
    diagnostics_figure,
    price_trend_figure,
    strategy_signal_figure,
    time_in_market_figure,
)
from python_stocks.dashboard.theme import DEFAULT_THEME_KEY, get_theme, page_style, surface_style


_SAMPLE = MarketSample.demo(["AAPL", "MSFT", "SPY", "QQQ"])


def _build_card(title: str, body: List[html.Div | dcc.Graph], theme_key: str) -> html.Div:
    theme = get_theme(theme_key)
    return html.Div(
        style=surface_style(theme),
        children=[
            html.H3(title, style={"marginTop": 0, "marginBottom": "12px"}),
            *body,
        ],
    )


def _overview_tab(theme_key: str) -> html.Div:
    return html.Div(
        className="grid",
        children=[
            _build_card(
                "Price Overview",
                [
                    dcc.Graph(
                        id="price-chart",
                        config={"displayModeBar": False},
                        style={"height": "360px"},
                    )
                ],
                theme_key,
            ),
            _build_card(
                "Strategy Lab",
                [
                    html.P("Moving average crossover vs. buy and hold."),
                    dcc.Graph(id="strategy-chart", style={"height": "360px"}, config={"displayModeBar": False}),
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
                    dcc.Graph(id="strategy-chart-secondary", style={"height": "400px"}, config={"displayModeBar": False}),
                    html.P("Signals derived from interactive moving-average helpers."),
                ],
                theme_key,
            ),
            _build_card(
                "Execution Context",
                [
                    dcc.Graph(id="cost-impact-chart-secondary", style={"height": "400px"}, config={"displayModeBar": False}),
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
                    dcc.Graph(id="cost-impact-chart", style={"height": "400px"}, config={"displayModeBar": False}),
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
                    dcc.Graph(id="time-in-market-chart", style={"height": "360px"}, config={"displayModeBar": False}),
                    html.P("Estimate of time spent participating in positive trends."),
                ],
                theme_key,
            ),
            _build_card(
                "Price Context",
                [dcc.Graph(id="price-chart-secondary", style={"height": "360px"}, config={"displayModeBar": False})],
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
                    dcc.Graph(id="diagnostics-chart", style={"height": "400px"}, config={"displayModeBar": False}),
                    html.P("Distribution of daily returns for sanity checks."),
                ],
                theme_key,
            ),
        ]
    )


def build_app() -> Dash:
    app = Dash(__name__, title="python-stocks dashboard", suppress_callback_exceptions=True)

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
                                style={"margin": 0, "color": get_theme(DEFAULT_THEME_KEY)["muted_text"]},
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Label("Theme", htmlFor="theme-toggle", style={"marginRight": "8px"}),
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
                    ),
                ],
            ),
            html.Div(
                style={"display": "flex", "gap": "12px", "marginBottom": "12px"},
                children=[
                    html.Div(
                        [
                            html.Label("Ticker"),
                            dcc.Dropdown(
                                id="ticker-dropdown",
                                options=[{"label": t, "value": t} for t in _SAMPLE.tickers],
                                value=_SAMPLE.tickers[0],
                                clearable=False,
                                style={"minWidth": "180px"},
                            ),
                        ]
                    ),
                ],
            ),
            dcc.Tabs(
                id="dashboard-tabs",
                value="overview",
                children=[
                    dcc.Tab(label="Overview", value="overview", children=[_overview_tab(DEFAULT_THEME_KEY)]),
                    dcc.Tab(label="Strategy Lab", value="strategy", children=[_strategy_tab(DEFAULT_THEME_KEY)]),
                    dcc.Tab(label="Cost/Impact Analysis", value="cost", children=[_cost_tab(DEFAULT_THEME_KEY)]),
                    dcc.Tab(label="Time in Market", value="timelesson", children=[_time_in_market_tab(DEFAULT_THEME_KEY)]),
                    dcc.Tab(label="Data Diagnostics", value="diagnostics", children=[_diagnostics_tab(DEFAULT_THEME_KEY)]),
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
        Input("ticker-dropdown", "value"),
        Input("theme-toggle", "value"),
    )
    def _update_charts(ticker: str, theme_key: str):
        theme = get_theme(theme_key)
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
        )

    return app


app = build_app()


if __name__ == "__main__":
    app.run_server(debug=True)
