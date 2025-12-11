
import numpy as np

from .math_helper import no_delay_moving_average_filter, slope
from .trading_history import TradingHistory

##### STRATEGIES
def strategy_no_investment(trading_history):
    return trading_history

def strategy_spy_asap_investment(trading_history):
    trading_history.buy_all_shares('SPY')
    return trading_history

def strategy_dia_asap_investment(trading_history):
    trading_history.buy_all_shares('DIA')
    return trading_history

def strategy_ndaq_asap_investment(trading_history):
    trading_history.buy_all_shares('NDAQ')
    return trading_history

def strategy_tqq_asap_investment(trading_history):
    trading_history.buy_all_shares('TQQQ')
    return trading_history

def strategy_marcus_2p25(trading_history):
    assert type(trading_history) is TradingHistory, "trading_history is not of type TradingHistory"

    interest = 2.25
    trading_history_day = 365
    daily_interest = interest/100/trading_history_day
    trading_history.trading_history_df['bank_account'][-1] += daily_interest*trading_history.trading_history_df['bank_account'][-1]

    return trading_history

def strategy_maf_investment(trading_history):
    assert type(trading_history) is TradingHistory, "trading_history is not of type TradingHistory"

    ##### Start with SPY.
    ticker = 'SPY'
    # ticker = 'TQQQ'
    spy_closing = trading_history.stock_df_to_today[ticker]['Close']
    spy_closing = list(spy_closing[~spy_closing.isin([np.nan, np.inf, -np.inf])])
    if len(spy_closing) < 2:
        return trading_history
    mafshort = no_delay_moving_average_filter(spy_closing, 10)
    mafshort_yesterday = no_delay_moving_average_filter(spy_closing[0:-1], 10)
    maflong = no_delay_moving_average_filter(spy_closing, 100)
    maflong_yesterday = no_delay_moving_average_filter(spy_closing[0:-1], 100)
    slope_mafshort = slope([mafshort_yesterday, mafshort], 2)
    slope_maflong = slope([maflong_yesterday, maflong], 2)

    if (spy_closing[-1] < mafshort) and (slope_maflong > 0):
        trading_history.buy_all_shares(ticker)
    if (mafshort > maflong) and (slope_mafshort < 0) and (spy_closing[-1] > mafshort):
        trading_history.sell_all_shares(ticker)

    return trading_history


def strategy_openclose_investment(trading_history):
    ticker = 'SPY'
    spy_closing = trading_history.stock_df_to_today[ticker]['Close']
    spy_closing = list(spy_closing[~spy_closing.isin([np.nan, np.inf, -np.inf])])
    spy_opening = trading_history.stock_df_to_today[ticker]['Open']
    spy_opening = list(spy_opening[~spy_opening.isin([np.nan, np.inf, -np.inf])])
    if len(spy_closing) < 2:
        return trading_history

    if spy_closing[-2] < spy_opening[-1]:
        trading_history.sell_all_shares(ticker, 'Open')
    else:
        trading_history.buy_all_shares(ticker, 'Open')

    return trading_history