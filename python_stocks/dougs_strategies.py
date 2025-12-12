import numpy as np

from .math_helper import no_delay_moving_average_filter, slope
from .services.strategy_service import StrategyContext
from .trading_history import TradingHistory


##### STRATEGIES


def _resolve_context(
    context: StrategyContext | TradingHistory, params: dict | None
) -> tuple[TradingHistory, dict]:
    if isinstance(context, StrategyContext):
        return context.history, context.params
    return context, params or {}


def strategy_no_investment(context: StrategyContext | TradingHistory, params: dict | None = None):
    history, _ = _resolve_context(context, params)
    return history


def strategy_buy_and_hold(context: StrategyContext | TradingHistory, params: dict | None = None):
    trading_history, params = _resolve_context(context, params)
    ticker = params.get("ticker", "SPY")
    when_to_buy = params.get("when", "Close")
    trading_history.buy_all_shares(ticker, when_to_buy)
    return trading_history


def strategy_marcus_2p25(context: StrategyContext | TradingHistory, params: dict | None = None):
    trading_history, params = _resolve_context(context, params)
    interest = params.get("interest_rate", 2.25)
    trading_history_day = 365
    daily_interest = interest / 100 / trading_history_day
    trading_history.trading_history_df["bank_account"][-1] += (
        daily_interest * trading_history.trading_history_df["bank_account"][-1]
    )

    return trading_history


def strategy_maf_investment(context: StrategyContext | TradingHistory, params: dict | None = None):
    trading_history, params = _resolve_context(context, params)
    ticker = params.get("ticker", "SPY")
    short_window = params.get("short_window", 10)
    long_window = params.get("long_window", 100)

    closing_prices = trading_history.stock_df_to_today[ticker]["Close"]
    closing_prices = list(closing_prices[~closing_prices.isin([np.nan, np.inf, -np.inf])])
    if len(closing_prices) < max(short_window, long_window):
        return trading_history

    mafshort = no_delay_moving_average_filter(closing_prices, short_window)
    mafshort_yesterday = no_delay_moving_average_filter(closing_prices[0:-1], short_window)
    maflong = no_delay_moving_average_filter(closing_prices, long_window)
    maflong_yesterday = no_delay_moving_average_filter(closing_prices[0:-1], long_window)
    slope_mafshort = slope([mafshort_yesterday, mafshort], 2)
    slope_maflong = slope([maflong_yesterday, maflong], 2)

    if (closing_prices[-1] < mafshort) and (slope_maflong > 0):
        trading_history.buy_all_shares(ticker)
    if (mafshort > maflong) and (slope_mafshort < 0) and (closing_prices[-1] > mafshort):
        trading_history.sell_all_shares(ticker)

    return trading_history


def strategy_openclose_investment(context: StrategyContext | TradingHistory, params: dict | None = None):
    trading_history, params = _resolve_context(context, params)
    ticker = params.get("ticker", "SPY")
    closing_prices = trading_history.stock_df_to_today[ticker]["Close"]
    closing_prices = list(closing_prices[~closing_prices.isin([np.nan, np.inf, -np.inf])])
    opening_prices = trading_history.stock_df_to_today[ticker]["Open"]
    opening_prices = list(opening_prices[~opening_prices.isin([np.nan, np.inf, -np.inf])])
    if len(closing_prices) < 2:
        return trading_history

    if closing_prices[-2] < opening_prices[-1]:
        trading_history.sell_all_shares(ticker, "Open")
    else:
        trading_history.buy_all_shares(ticker, "Open")

    return trading_history
