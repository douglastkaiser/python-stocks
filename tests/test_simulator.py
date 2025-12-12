import pandas as pd

from python_stocks.engine.simulator import SimulationEngine, render_summary_artifacts
from python_stocks.registry_factory import build_default_registry
from python_stocks.stock_data import StockData


class _InMemoryLoader:
    def __init__(self, frames):
        self.frames = frames

    def __call__(self, ticker):
        return self.frames[ticker]


def _build_stock_data():
    dates = pd.date_range("2020-01-01", periods=6, freq="D")
    base = pd.DataFrame(
        {"Open": [10, 10.5, 11, 11.5, 12, 12.5], "Close": [10, 10.6, 10.8, 11.2, 11.4, 11.8]}, index=dates
    )
    loader = _InMemoryLoader({"AAA": base, "BBB": base * 1.02})
    return StockData(["AAA", "BBB"], loader=loader)


def test_simulation_engine_runs_with_seed(tmp_path):
    stock_data = _build_stock_data()
    engine = SimulationEngine(stock_data, registry=build_default_registry(stock_data.tickers()))

    first_output = engine.run_once(1000, seed=123)
    second_output = engine.run_once(1000, seed=123)

    assert first_output.report_df.equals(second_output.report_df)
    assert first_output.results[0].trade_count == second_output.results[0].trade_count

    artifacts = render_summary_artifacts(first_output, tmp_path)
    assert artifacts["summary_html"].exists()
    assert artifacts["summary_html"].read_text()
    for path in artifacts.values():
        assert path.exists()
        assert path.stat().st_size > 0


def test_batch_runs_collect_multiple_seeds():
    stock_data = _build_stock_data()
    engine = SimulationEngine(stock_data, registry=build_default_registry(stock_data.tickers()))

    outputs = engine.run_batch(500, seeds=[1, 2])

    assert len(outputs) == 2
    assert outputs[0].report_df.shape == outputs[1].report_df.shape
    assert outputs[0].results[0].strategy == outputs[1].results[0].strategy
