import pandas as pd

from python_stocks.dougs_strategies import (
    strategy_buy_and_hold,
    strategy_maf_investment,
    strategy_marcus_2p25,
    strategy_no_investment,
    strategy_openclose_investment,
)
from python_stocks.trading_history import TradingHistory
from pytest import approx


def _build_history(prices):
    stock_df = pd.concat([prices], axis=1, keys=["AAA"])
    history = TradingHistory(
        ["AAA", "bank_account", "money_invested"],
        principal=0,
        strat_function=lambda h: h,
        name="test",
    )
    history.stock_df_to_today = stock_df
    history.trading_history_df = pd.DataFrame(
        {"AAA": [0] * len(stock_df), "bank_account": [100.0] * len(stock_df), "money_invested": [0] * len(stock_df)},
        index=stock_df.index,
    )
    return history


def test_strategy_no_investment_is_noop():
    prices = pd.DataFrame({"Close": [10.0]}, index=pd.date_range("2020-01-01", periods=1))
    history = _build_history(prices)

    updated = strategy_no_investment(history, {})

    assert updated.trading_history_df.equals(history.trading_history_df)


def test_strategy_buy_and_hold_purchases_shares():
    prices = pd.DataFrame({"Close": [10.0]}, index=pd.date_range("2020-01-01", periods=1))
    history = _build_history(prices)

    strategy_buy_and_hold(history, {"ticker": "AAA", "when": "Close"})

    assert history.trading_history_df.at[prices.index[0], "AAA"] == 10
    assert history.trading_history_df.at[prices.index[0], "bank_account"] == 0


def test_strategy_marcus_accrues_interest():
    prices = pd.DataFrame({"Close": [10.0]}, index=pd.date_range("2020-01-01", periods=1))
    history = _build_history(prices)

    strategy_marcus_2p25(history, {"interest_rate": 3.65})

    expected_growth = 100.0 * (3.65 / 100 / 365)
    assert history.trading_history_df.at[prices.index[0], "bank_account"] == approx(100.0 + expected_growth)


def test_strategy_maf_triggers_buy_on_crossover(monkeypatch):
    prices = pd.DataFrame({"Close": [1.0, 2.0, 3.0, 2.5]}, index=pd.date_range("2020-01-01", periods=4))
    history = _build_history(prices)
    buy_calls = []
    monkeypatch.setattr(history, "buy_all_shares", lambda *args, **kwargs: buy_calls.append(args))
    monkeypatch.setattr(
        "python_stocks.dougs_strategies.no_delay_moving_average_filter",
        lambda data, window: 5.0 if window == 2 else 4.0,
    )
    monkeypatch.setattr("python_stocks.dougs_strategies.slope", lambda *_args, **_kwargs: 1.0)

    strategy_maf_investment(
        history,
        {"ticker": "AAA", "short_window": 2, "long_window": 3},
    )

    assert buy_calls, "Expected moving average filter to trigger a buy"


def test_strategy_openclose_uses_prior_close_vs_open(monkeypatch):
    prices = pd.DataFrame({"Close": [1.0, 0.5]}, index=pd.date_range("2020-01-01", periods=2))
    opens = pd.DataFrame({"Open": [1.1, 1.2]}, index=prices.index)
    stock_df = pd.concat([prices, opens], axis=1)
    stock_df = pd.concat([stock_df], axis=1, keys=["AAA"])

    history = TradingHistory(
        ["AAA", "bank_account", "money_invested"],
        principal=0,
        strat_function=lambda h: h,
        name="test",
    )
    history.stock_df_to_today = stock_df
    history.trading_history_df = pd.DataFrame(
        {"AAA": [5, 5], "bank_account": [0.0, 0.0], "money_invested": [0, 0]}, index=prices.index
    )

    sell_calls = []
    buy_calls = []
    monkeypatch.setattr(history, "sell_all_shares", lambda *args, **kwargs: sell_calls.append(args))
    monkeypatch.setattr(history, "buy_all_shares", lambda *args, **kwargs: buy_calls.append(args))

    strategy_openclose_investment(history, {"ticker": "AAA"})

    assert sell_calls, "Expected a sell signal when prior close is below current open"
    assert not buy_calls
