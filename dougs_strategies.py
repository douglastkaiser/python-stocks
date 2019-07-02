
from TradingDay import TradingDay
from math_helper import *

#### STRATEGIES
def strategy_no_investment(trading_day):
    assert type(trading_day) is TradingDay, "trading_day is not of type TradingDay"

    return trading_day

def strategy_asap_investment(trading_day):
    assert type(trading_day) is TradingDay, "trading_day is not of type TradingDay"

    trading_day.buy_all_shares()
    return trading_day

def strategy_marcus_2p25(trading_day):
    assert type(trading_day) is TradingDay, "trading_day is not of type TradingDay"

    interest = 2.25
    trading_days = 252
    trading_day.bank_account_history[-1] += interest/100*trading_day.bank_account_history[-1]/trading_days

    return trading_day

def strategy_sinusoid_investment(trading_day):
    assert type(trading_day) is TradingDay, "trading_day is not of type TradingDay"

    close_prices = trading_day.price_history

    days_prev = len(close_prices)
    prev_close_price_1 = close_prices[max([days_prev-3, 0])]
    prev_close_price_2 = close_prices[max([days_prev-2, 0])]
    prev_close_price_3 = close_prices[max([days_prev-1, 0])]
    latest_close_price = close_prices[-1]

    if (prev_close_price_1 <= latest_close_price) and (prev_close_price_1 <= prev_close_price_2) and (prev_close_price_2 <= prev_close_price_3):
        trading_day.buy_all_shares()
    elif (prev_close_price_1 >= latest_close_price) and (prev_close_price_1 >= prev_close_price_2) and (prev_close_price_2 >= prev_close_price_3):
        trading_day.sell_one_share()
    return trading_day

def strategy_maf_investment(trading_day):
    assert type(trading_day) is TradingDay, "trading_day is not of type TradingDay"

    mafshort = no_delay_moving_average_filter(trading_day.price_history, 10)
    mafshort_yesterday = no_delay_moving_average_filter(trading_day.price_history[0:-1], 10)
    maflong = no_delay_moving_average_filter(trading_day.price_history, 100)

    slope_mafshort = slope([mafshort_yesterday, mafshort], 2)

    if (trading_day.price_history[-1] < mafshort):
        trading_day.buy_all_shares()
    if (mafshort > maflong) and (slope_mafshort < 0) and (trading_day.price_history[-1] > mafshort):
        trading_day.sell_all_shares()

    return trading_day
