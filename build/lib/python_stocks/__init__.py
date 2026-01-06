"""Trading strategy simulations for historical stock data."""

__all__ = [
    "main",
    "run_simulation",
    "StockData",
    "TradingHistory",
]


def main(argv=None):
    from .cli import main as _main

    return _main(argv)


def run_simulation(*args, **kwargs):
    from .main import run_simulation as _run_simulation

    return _run_simulation(*args, **kwargs)


def StockData(*args, **kwargs):
    from .stock_data import StockData as _StockData

    return _StockData(*args, **kwargs)


def TradingHistory(*args, **kwargs):
    from .trading_history import TradingHistory as _TradingHistory

    return _TradingHistory(*args, **kwargs)
