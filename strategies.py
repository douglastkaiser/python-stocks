
def run_all_strategies(initial_deposit, daily_investment, close_prices):
    print("Initial Deposit: " + str(initial_deposit))
    print("Daily Investment: " + str(daily_investment))

    strategy_no_investment_trading_day = TradingDay(0, initial_deposit, [0])
    for close_price in close_prices:
        strategy_no_investment_trading_day = strategy_no_investment(strategy_no_investment_trading_day)


    printer(strategy_no_investment_trading_day):

def buy_one_share(trading_day):
    if trading_day.price_history[-1] < trading_day.bank_account
        trading_day.shares_owned = trading_day.shares_owned + 1
        trading_day.bank_account = trading_day.bank_account - trading_day.price_history[-1]
    return trading_day

def sell_one_share(trading_day):
    if trading_day.shares_owned > 0
        trading_day.shares_owned = trading_day.shares_owned - 1
        trading_day.bank_account = trading_day.bank_account + trading_day.price_history[-1]
    return trading_day

def strategy_no_investment(trading_day):
    return 0

def printer(end_trading_day):
    print("\n -- Strat = _______ --")
    print("Shares Owned in end: " + str(end_trading_day.shares_owned))
    print("Bank Account left over: " + str(end_trading_day.bank_account))
    protfolio_value = end_trading_day.shares_owned*end_trading_day.price_history[-1] + end_trading_day.bank_account
    print("Total Value: " + str(protfolio_value))