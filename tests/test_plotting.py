import importlib


def test_plotting_switches_to_agg_backend(monkeypatch):
    monkeypatch.setenv("PYTHON_STOCKS_TEST_MODE", "1")
    plotting = importlib.reload(importlib.import_module("python_stocks.plotting"))

    assert plotting.TEST_MODE_FLAG is True
    assert plotting.plt.get_backend().lower() == "agg"
