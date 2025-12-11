import pandas as pd
import pytest

from python_stocks.data_loading import load_into_stock_data_set


def test_loads_with_optional_columns(tmp_path):
    data = pd.DataFrame(
        {
            "Date": pd.date_range("2020-01-01", periods=3, freq="D"),
            "Open": [1.0, 2.0, 3.0],
            "High": [1.5, 2.5, 3.5],
            "Low": [0.5, 1.5, 2.5],
            "Close": [1.2, 2.2, 3.2],
            "Volume": [10, 11, 12],
        }
    )
    csv_path = tmp_path / "sample.csv"
    data.to_csv(csv_path, index=False)

    df = load_into_stock_data_set("sample", data_dir=tmp_path)

    assert list(df.columns) == ["Close", "Open", "High", "Low", "Volume"]
    assert df.index.is_monotonic_increasing


def test_missing_optional_columns_are_added(tmp_path):
    data = pd.DataFrame(
        {
            "Date": ["2020-01-01", "2020-01-02"],
            "Open": [1.0, 2.0],
            "Close": [1.1, 2.1],
        }
    )
    csv_path = tmp_path / "partial.csv"
    data.to_csv(csv_path, index=False)

    df = load_into_stock_data_set("partial", data_dir=tmp_path)

    assert "High" in df.columns and df["High"].isna().all()
    assert "Low" in df.columns and df["Low"].isna().all()
    assert "Volume" in df.columns and df["Volume"].isna().all()


def test_rejects_missing_required_columns(tmp_path):
    data = pd.DataFrame({"Date": ["2020-01-01"], "Open": [1.0]})
    (tmp_path / "invalid.csv").write_text(data.to_csv(index=False))

    with pytest.raises(ValueError, match="missing required columns"):
        load_into_stock_data_set("invalid", data_dir=tmp_path)


def test_rejects_duplicate_dates(tmp_path):
    data = pd.DataFrame(
        {
            "Date": ["2020-01-01", "2020-01-01"],
            "Open": [1.0, 1.0],
            "Close": [1.1, 1.1],
        }
    )
    (tmp_path / "dupe.csv").write_text(data.to_csv(index=False))

    with pytest.raises(ValueError, match="duplicate dates"):
        load_into_stock_data_set("dupe", data_dir=tmp_path)


def test_rejects_non_monotonic_dates(tmp_path):
    data = pd.DataFrame(
        {
            "Date": ["2020-01-02", "2020-01-01"],
            "Open": [2.0, 1.0],
            "Close": [2.1, 1.1],
        }
    )
    (tmp_path / "unordered.csv").write_text(data.to_csv(index=False))

    with pytest.raises(ValueError, match="strictly increasing order"):
        load_into_stock_data_set("unordered", data_dir=tmp_path)


def test_fetcher_is_used_when_provided():
    fetch_called = False

    def fetcher(name: str) -> pd.DataFrame:
        nonlocal fetch_called
        fetch_called = True
        return pd.DataFrame(
            {
                "Date": ["2020-01-01", "2020-01-02"],
                "Open": [1.0, 2.0],
                "Close": [1.1, 2.1],
            }
        )

    df = load_into_stock_data_set("ignored", fetcher=fetcher)

    assert fetch_called is True
    assert df.index.is_monotonic_increasing
