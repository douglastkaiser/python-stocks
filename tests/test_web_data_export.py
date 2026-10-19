"""Check that the shipped browser data is valid and uses adjusted prices."""

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "export_web_data.py"
spec = importlib.util.spec_from_file_location("export_web_data", SCRIPT)
assert spec and spec.loader
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


def test_export_preserves_coverage_and_adjusted_prices(tmp_path):
    exporter.export(tmp_path)
    for ticker in exporter.SYMBOLS:
        data = json.loads((tmp_path / f"{ticker}.json").read_text())
        assert data["ticker"] == ticker
        assert data["mode"] == "historical"
        assert data["end"] == "2019-07-02"
        assert len(data["prices"]) > 2000
        assert data["start"] == data["prices"][0]["date"]
        assert data["end"] == data["prices"][-1]["date"]
    spy = json.loads((tmp_path / "SPY.json").read_text())
    assert spy["prices"][0]["close"] == pytest.approx(26.706753)


@pytest.mark.parametrize(
    "rows",
    [
        "2018-01-01,0",
        "2018-01-01,nan",
        "2018-01-02,1\n2018-01-01,2",
        "2018-01-01,1\n2018-01-01,2",
    ],
)
def test_export_rejects_bad_history(tmp_path, monkeypatch, rows):
    raw = tmp_path / "python_stocks" / "raw_data"
    raw.mkdir(parents=True)
    (raw / "SPY.csv").write_text("Date,Adj Close\n" + rows + "\n")
    monkeypatch.setattr(exporter, "ROOT", tmp_path)
    monkeypatch.setattr(exporter, "SYMBOLS", {"SPY": "Fixture"})
    with pytest.raises(ValueError, match="Invalid or unordered"):
        exporter.export(tmp_path / "output")
