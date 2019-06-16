
from TradingDay import TradingDay

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
    shares_owned = trading_day.shares_history[-1]

    days_prev = len(close_prices)
    prev_close_price_1 = close_prices[max([days_prev-3, 0])]
    prev_close_price_2 = close_prices[max([days_prev-2, 0])]
    prev_close_price_3 = close_prices[max([days_prev-1, 0])]
    latest_close_price = close_prices[-1]

    if (prev_close_price_1 < latest_close_price) and (prev_close_price_1 < prev_close_price_2) and (prev_close_price_2 < prev_close_price_3):
        trading_day.buy_all_shares()
    elif (prev_close_price_1 > latest_close_price) and (prev_close_price_1 > prev_close_price_2) and (prev_close_price_2 > prev_close_price_3):
        trading_day.sell_one_share()
    return trading_day

def strategy_maf_investment(trading_day):
    assert type(trading_day) is TradingDay, "trading_day is not of type TradingDay"

    maf_average = trading_day.maf(5)
    if (trading_day.price_history[-1] < maf_average):
        trading_day.buy_all_shares()

    maf_average = trading_day.maf(300)
    if (trading_day.price_history[-1] > maf_average):
        trading_day.sell_one_share()

    return trading_day
