import pandas as pd

from python_stocks import stock_data as stock_data_module
from python_stocks.stock_data import StockData


def _make_stub_df():
    dates = pd.date_range("2020-01-01", periods=4, freq="D")
    return pd.DataFrame(
        {"Date": dates, "Close": [1.0, 2.0, 3.0, 4.0], "Open": [1.0, 2.0, 3.0, 4.0]}
    )


def test_get_stock_df_to_today_and_money_to_add(monkeypatch):
    stub_df = _make_stub_df().set_index("Date")
    monkeypatch.setattr(
        stock_data_module, "load_into_stock_data_set", lambda _: stub_df
    )

    stock_data = StockData(["AAA"], monthly_deposit=100, daily_deposit=10)

    first_slice, first_deposit = stock_data.get_stock_df_to_today_and_money_to_add(1)
    assert first_slice.index[-1].day == 1
    assert first_deposit == 110

    second_slice, second_deposit = stock_data.get_stock_df_to_today_and_money_to_add(2)
    assert len(second_slice) == 2
    assert second_deposit == 10


def test_limit_timeframe_trims_bounds(monkeypatch):
    stub_df = _make_stub_df().set_index("Date")
    monkeypatch.setattr(
        stock_data_module, "load_into_stock_data_set", lambda _: stub_df
    )

    stock_data = StockData(["AAA"])
    stock_data.limit_timeframe("2020-01-02", "2020-01-03")

    assert list(stock_data.data_frame.index) == list(
        pd.date_range("2020-01-02", periods=2, freq="D")
    )
