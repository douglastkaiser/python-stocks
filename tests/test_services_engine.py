import importlib
from typing import Dict, cast

import pandas as pd
import pytest

from python_stocks.engine.simulator import _compute_metrics
from python_stocks.services import runtime_flags
from python_stocks.services.data_service import DataService
from python_stocks.trading_history import TradingHistory


def _fake_history() -> Dict[str, pd.DataFrame]:
    dates = pd.date_range("2020-01-01", periods=3, freq="D")
    price_frame = pd.DataFrame({"Close": [100.0, 110.0, 105.0]}, index=dates)
    history = pd.DataFrame(
        {
            "AAA": [0, 1, 1],
            "bank_account": [1000.0, 500.0, 520.0],
            "money_invested": [1000.0, 0.0, 0.0],
        },
        index=dates,
    )
    return {"frame": price_frame, "history": history}


class _StubHistory:
    def __init__(self) -> None:
        snapshots = _fake_history()
        self.trading_history_df = snapshots["history"]
        self.stock_df_to_today = {"AAA": snapshots["frame"]}
        self.total_fees: float = 5.0
        self.total_slippage_cost: float = 2.5

    def portfolio_value_history(self):
        return [1000.0, 1110.0, 1150.0]


def test_compute_metrics_tracks_trades_and_penalties():
    history = _StubHistory()

    metrics = _compute_metrics(
        cast(TradingHistory, history),
        ["AAA"],
        benchmark_ticker="AAA",
        time_in_market_penalty_rate=0.1,
    )

    assert metrics["trade_count"] == 1
    assert metrics["time_in_market_ratio"] == pytest.approx(2 / 3)
    assert metrics["time_in_market_penalty"] == pytest.approx(-0.0666666, rel=1e-3)
    assert metrics["tracking_error"] >= 0


def test_prefer_cached_results_env_flags(monkeypatch):
    monkeypatch.setenv("PYTHON_STOCKS_LIVE_COMPUTE", "1")
    reloaded_flags = importlib.reload(runtime_flags)
    assert reloaded_flags.prefer_cached_results() is False

    monkeypatch.delenv("PYTHON_STOCKS_LIVE_COMPUTE")
    monkeypatch.setenv("PYTHON_STOCKS_STATIC_ARTIFACTS", "1")
    reloaded_flags = importlib.reload(runtime_flags)
    assert reloaded_flags.prefer_cached_results() is True
    assert reloaded_flags.prefer_cached_results(opt_in=False) is False
    monkeypatch.delenv("PYTHON_STOCKS_STATIC_ARTIFACTS")


def test_data_service_uses_cache_and_refresh(monkeypatch, tmp_path):
    load_calls = []

    def _fake_loader(ticker, data_dir=None, fetcher=None):
        load_calls.append(ticker)
        return pd.DataFrame({"Close": [1.0, 2.0, 3.0]})

    monkeypatch.setattr(
        "python_stocks.services.data_service.load_into_stock_data_set", _fake_loader
    )
    monkeypatch.setattr(
        "python_stocks.services.data_service.prefer_cached_results",
        lambda opt_in=None: True,
    )

    service = DataService(data_dir=tmp_path)

    first = service.load_dataset("AAA")
    first.loc[0, "Close"] = 99.0
    second = service.load_dataset("AAA")
    third = service.load_dataset("AAA", force_refresh=True)

    assert len(load_calls) == 2
    assert first.loc[1, "Close"] == 2.0
    assert second.loc[1, "Close"] == 2.0
    assert third.loc[1, "Close"] == 2.0
    assert second is not first
    assert third is not second
