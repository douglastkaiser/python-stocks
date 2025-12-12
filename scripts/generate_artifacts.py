"""Generate simulation outputs and Plotly snapshots for CI artifacts."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Iterable, Tuple

from python_stocks.dashboard.components import (
    MarketSample,
    comparison_matrix_figure,
    cost_impact_figure,
    diagnostics_figure,
    price_trend_figure,
    strategy_signal_figure,
    time_in_market_figure,
    timeline_overlay_figure,
)
from python_stocks.dashboard.theme import DEFAULT_THEME_KEY, get_theme
from python_stocks.main import run_simulation


def _ensure_test_mode() -> None:
    """Force a headless plotting backend for CI environments."""

    os.environ.setdefault("PYTHON_STOCKS_TEST_MODE", "1")


def _run_core_simulation(output_dir: Path) -> None:
    """Execute a fast sample simulation and persist tabular outputs."""

    output_dir.mkdir(parents=True, exist_ok=True)
    run_simulation(
        tickers=["SPY", "DIA"],
        start_date="2017-01-01",
        end_date="2018-01-01",
        initial_deposit=50_000,
        daily_deposit=0,
        monthly_deposit=500,
        strategies=["buy_and_hold"],
        parameter_overrides=None,
        report_dir=str(output_dir),
        show_plots=False,
    )


def _plotly_snapshots(sample: MarketSample, ticker: str, output_dir: Path) -> Iterable[Tuple[str, Path]]:
    """Build Plotly HTML/PNG exports for the dashboard demo figures."""

    theme = get_theme(DEFAULT_THEME_KEY)
    output_dir.mkdir(parents=True, exist_ok=True)

    figures = {
        "price_trend": price_trend_figure(sample, ticker, theme),
        "strategy_signal": strategy_signal_figure(sample, ticker, theme),
        "cost_impact": cost_impact_figure(sample, ticker, theme),
        "comparison_matrix": comparison_matrix_figure(sample, ticker, theme),
        "timeline_overlay": timeline_overlay_figure(sample, ticker, theme),
        "time_in_market": time_in_market_figure(sample, ticker, theme),
        "diagnostics": diagnostics_figure(sample, ticker, theme),
    }

    for name, fig in figures.items():
        html_path = output_dir / f"{name}.html"
        png_path = output_dir / f"{name}.png"
        fig.write_html(str(html_path), include_plotlyjs="cdn", full_html=True)
        fig.write_image(str(png_path), format="png", width=1024, height=640, scale=2)
        yield name, html_path
        yield name, png_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate demo assets for CI uploads.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts"),
        help="Destination directory for saved reports and Plotly snapshots.",
    )
    args = parser.parse_args()

    _ensure_test_mode()

    simulation_dir = args.output_dir / "simulation"
    plotly_dir = args.output_dir / "plotly"

    _run_core_simulation(simulation_dir)

    sample = MarketSample.demo(["AAPL", "MSFT", "SPY"], periods=120)
    list(_plotly_snapshots(sample, ticker="AAPL", output_dir=plotly_dir))


if __name__ == "__main__":
    main()
