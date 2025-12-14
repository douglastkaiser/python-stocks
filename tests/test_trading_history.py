import numpy as np
import pandas as pd

from python_stocks.trading_history import TradingHistory


def _noop_strategy(history: TradingHistory) -> TradingHistory:
    return history


def test_current_portfolio_value_uses_last_valid_price():
    dates = pd.date_range("2020-01-01", periods=3)
    prices = pd.DataFrame({"Close": [10.0, np.nan, 12.0]}, index=dates)
    stock_df = pd.concat([prices], axis=1, keys=["AAA"])

    trading_history = TradingHistory(
        ["AAA", "bank_account", "money_invested"],
        principal=0,
        strat_function=_noop_strategy,
        name="test",
    )
    trading_history.stock_df_to_today = stock_df
    trading_history.trading_history_df = pd.DataFrame(
        {"AAA": [1, 1, 1], "bank_account": [0, 0, 0], "money_invested": [0, 0, 0]},
        index=dates,
    )

    value_with_nan_price = trading_history.current_portfolio_value(1)

    assert value_with_nan_price == 10.0


def test_buy_all_shares_respects_cash_and_costs():
    dates = pd.date_range("2020-01-01", periods=1)
    prices = pd.DataFrame({"Close": [10.0]}, index=dates)
    stock_df = pd.concat([prices], axis=1, keys=["AAA"])

    trading_history = TradingHistory(
        ["AAA", "bank_account", "money_invested"],
        principal=0,
        strat_function=_noop_strategy,
        name="test",
        transaction_cost_rate=0.1,
    )
    trading_history.stock_df_to_today = stock_df
    trading_history.trading_history_df = pd.DataFrame(
        {"AAA": [0], "bank_account": [100.0], "money_invested": [0]},
        index=dates,
    )

    trading_history.buy_all_shares("AAA")

    assert trading_history.trading_history_df.at[dates[0], "AAA"] == 9
    assert trading_history.trading_history_df.at[dates[0], "bank_account"] >= 0


def test_returns_and_drawdown_calculations():
    dates = pd.date_range("2020-01-01", periods=3)
    prices = pd.DataFrame({"Close": [10.0, 11.0, 12.0]}, index=dates)
    stock_df = pd.concat([prices], axis=1, keys=["AAA"])

    trading_history = TradingHistory(
        ["AAA", "bank_account", "money_invested"],
        principal=100,
        strat_function=_noop_strategy,
        name="test",
    )
    trading_history.stock_df_to_today = stock_df
    trading_history.trading_history_df = pd.DataFrame(
        {
            "AAA": [0, 5, 5],
            "bank_account": [100.0, 45.0, 45.0],
            "money_invested": [100.0, 0.0, 0.0],
        },
        index=dates,
    )

    twr = trading_history.time_weighted_return(annualize=False)
    mwr = trading_history.money_weighted_return(annualize=False)
    drawdown = trading_history.drawdown_series()

    assert round(twr, 4) == 0.05
    assert round(mwr, 4) == round((1.05 ** (1 / 3)) - 1, 4)
    assert drawdown.min() == 0


def test_new_day_applies_principal_and_deposits():
    dates = pd.date_range("2020-01-01", periods=2)
    prices = pd.DataFrame({"Close": [10.0, 11.0]}, index=dates)
    stock_df = pd.concat([prices], axis=1, keys=["AAA"])

    trading_history = TradingHistory(
        ["AAA", "bank_account", "money_invested"],
        principal=50,
        strat_function=_noop_strategy,
        name="test",
    )

    trading_history.new_day(stock_df.iloc[:1], money_to_add=25)
    assert trading_history.trading_history_df.at[dates[0], "bank_account"] == 75

    trading_history.new_day(stock_df, money_to_add=10)
    assert trading_history.trading_history_df.at[dates[1], "bank_account"] == 85


def test_sell_all_shares_applies_slippage_and_costs():
    dates = pd.date_range("2020-01-01", periods=1)
    prices = pd.DataFrame({"Close": [10.0]}, index=dates)
    stock_df = pd.concat([prices], axis=1, keys=["AAA"])

    trading_history = TradingHistory(
        ["AAA", "bank_account", "money_invested"],
        principal=0,
        strat_function=_noop_strategy,
        name="test",
        transaction_cost_rate=0.05,
        slippage_pct=0.01,
    )
    trading_history.stock_df_to_today = stock_df
    trading_history.trading_history_df = pd.DataFrame(
        {"AAA": [2], "bank_account": [0.0], "money_invested": [0]}, index=dates
    )

    trading_history.sell_all_shares("AAA")

    expected_sale_price = 10.0 * (1 - 0.01)
    expected_trade_value = expected_sale_price * 2
    expected_cost = expected_trade_value * 0.05
    assert (
        trading_history.trading_history_df.at[dates[0], "bank_account"]
        == expected_trade_value - expected_cost
    )
    assert trading_history.trading_history_df.at[dates[0], "AAA"] == 0
