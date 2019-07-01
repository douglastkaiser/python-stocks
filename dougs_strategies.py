
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

    mafshort = no_delay_moving_average_filter_vectorized(trading_day.price_history, 1)
    maflong = no_delay_moving_average_filter_vectorized(trading_day.price_history, 50)
    # slope_mafshort = no_delay_moving_average_filter_vectorized(slope_vectorized(mafshort), 10)
    # curvature_mafshort = no_delay_moving_average_filter_vectorized(curvature_vectorized(mafshort), 10)
    slope_mafshort = slope(trading_day.price_history, 2)
    # slope_maflong = slope(maflong, 5)
    # curvature_mafshort = curvature(mafshort)

    # if (mafshort < maflong):
    #     trading_day.buy_all_shares()
    # if (mafshort > maflong):
    #     trading_day.sell_all_shares()

    # percent_diff = percentage_difference(maflong, mafshort)
    # if (percent_diff > 2):
    #     trading_day.buy_all_shares()
    # if (percent_diff < -2):
    #     trading_day.sell_all_shares()

    # if (curvature_mafshort > 0) and (slope_mafshort > 0) and (mafshort[-1] < maflong[-1]):
    #     trading_day.buy_all_shares()
    # if (curvature_mafshort < 0) and (slope_mafshort < 0) and (mafshort[-1] > maflong[-1]):
    #     trading_day.sell_all_shares()

    trading_day.buy_all_shares()
    if (mafshort[-1] < maflong[-1]) and (slope_mafshort < 0):
        trading_day.sell_all_shares()

    # if (slope_mafshort < 0):
    #     trading_day.buy_all_shares()
    # if (slope_mafshort > 0):
    #     trading_day.sell_all_shares()

    # if (mafshort[-1] < maflong[-1]) and (slope_maflong < 0):
    #     trading_day.sell_all_shares()
    # if (mafshort[-1] > maflong[-1]):
    #     trading_day.buy_all_shares()

    # trading_day.buy_all_shares()
    # if (slope_maflong < 0):
    #     trading_day.sell_all_shares()
    # if (slope_mafshort > 0):
    #     trading_day.buy_all_shares()

    # if (curvature_mafshort > 0) and (slope_mafshort > 0):
    #     trading_day.buy_all_shares()
    # if (curvature_mafshort < 0) and (slope_mafshort < 0):
    #     trading_day.sell_all_shares()

    return trading_day
