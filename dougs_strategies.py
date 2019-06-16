#### STRATEGIES
def strategy_no_investment(trading_day):
    assert type(trading_day) is TradingDay, "trading_day is not of type TradingDay"

    return trading_day

def strategy_asap_investment(trading_day):
    assert type(trading_day) is TradingDay, "trading_day is not of type TradingDay"

    trading_day.buy_all_shares()
    return trading_day

def strategy_sinusoid_investment(trading_day):
    assert type(trading_day) is TradingDay, "trading_day is not of type TradingDay"

    close_prices = trading_day.price_history
    bank_account = trading_day.bank_account
    shares_owned = trading_day.shares_owned

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

    maf_n = 50
    prices = trading_day.price_history
    latest_i = len(prices)
    oldest_i = min([len(prices)-maf_n, 0])
    prices_in_window = prices[oldest_i:latest_i]
    maf_average = sum(prices_in_window) / maf_n

    if (prices[-1] < maf_average):
        trading_day.buy_all_shares()

    maf_n = 200
    oldest_i = min([len(prices)-maf_n, 0])
    prices_in_window = prices[oldest_i:latest_i]
    maf_average = sum(prices_in_window) / maf_n
    # if (prices[-1] < maf_average):
        # trading_day.sell_one_share()

    return trading_day
