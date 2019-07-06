
from TradingHistory import TradingHistory
from math_helper import *

#### STRATEGIES
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
    trading_historys = 252
    trading_history.bank_account_history[-1] += interest/100*trading_history.bank_account_history[-1]/trading_historys

    return trading_history

def strategy_maf_investment(trading_history):
    assert type(trading_history) is TradingHistory, "trading_history is not of type TradingHistory"

    # Start with SPY.
    trading_history.trading_history_df['SPY']['Close']
    mafshort = no_delay_moving_average_filter(trading_history.price_history, 10)
    mafshort_yesterday = no_delay_moving_average_filter(trading_history.price_history[0:-1], 10)
    maflong = no_delay_moving_average_filter(trading_history.price_history, 100)
    maflong_yesterday = no_delay_moving_average_filter(trading_history.price_history[0:-1], 100)
    slope_mafshort = slope([mafshort_yesterday, mafshort], 3)
    slope_maflong = slope([maflong_yesterday, maflong], 3)

    if (trading_history.price_history[-1] < mafshort) and (slope_maflong > 0):
        trading_history.buy_all_shares()
    if (mafshort > maflong) and (slope_mafshort < 0) and (trading_history.price_history[-1] > mafshort):
        trading_history.sell_all_shares()

    return trading_history
