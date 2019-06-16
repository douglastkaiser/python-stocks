
from TradingDay import TradingDay
import matplotlib.pyplot as plt
import numpy as np
from dougs_strategies import *

def run_dougs_strategies(initial_deposit, daily_investment, close_prices):
    print("Initial Deposit: " + str(initial_deposit))
    print("Daily Investment: " + str(daily_investment))

    fig = plt.figure()  # an empty figure with no axes
    fig.suptitle('No axes on this figure')  # Add a title so we know which it is
    x = np.linspace(0, 2, len(close_prices))

    plt.plot(x, close_prices, label='Closing Prices')
    plt.xlabel('x label')
    plt.ylabel('y label')
    plt.title("Simple Plot")
    plt.legend()
    # plt.show()

    strategy_no_investment_trading_day = TradingDay([0], [initial_deposit], close_prices[0])
    strategy_asap_investment_trading_day = TradingDay([0], [initial_deposit], close_prices[0])
    strategy_sinusoid_investment_trading_day = TradingDay([0], [initial_deposit], close_prices[0])
    strategy_maf_investment_trading_day = TradingDay([0], [initial_deposit], close_prices[0])

    # for close_price in close_prices:
    for i in range(1, len(close_prices)):
        price_history_today = close_prices[0:i]
        # print(len(price_history_today))

        strategy_no_investment_trading_day.update_price_history(price_history_today)
        strategy_no_investment_trading_day.add_daily_investment(daily_investment)
        strategy_no_investment_trading_day = strategy_no_investment(strategy_no_investment_trading_day)

        strategy_asap_investment_trading_day.update_price_history(price_history_today)
        strategy_asap_investment_trading_day.add_daily_investment(daily_investment)
        strategy_asap_investment_trading_day = strategy_asap_investment(strategy_asap_investment_trading_day)

        strategy_sinusoid_investment_trading_day.update_price_history(price_history_today)
        strategy_sinusoid_investment_trading_day.add_daily_investment(daily_investment)
        strategy_sinusoid_investment_trading_day = strategy_sinusoid_investment(strategy_sinusoid_investment_trading_day)

        strategy_maf_investment_trading_day.update_price_history(price_history_today)
        strategy_maf_investment_trading_day.add_daily_investment(daily_investment)
        strategy_maf_investment_trading_day = strategy_maf_investment(strategy_maf_investment_trading_day)
        
    print("\n -- Strat = NONE --")
    strategy_no_investment_trading_day.printer()

    print("\n -- Strat = ASAP --")
    strategy_asap_investment_trading_day.printer()

    print("\n -- Strat = SINUSOID --")
    strategy_sinusoid_investment_trading_day.printer()

    print("\n -- Strat = 100pt MAF --")
    strategy_maf_investment_trading_day.printer()
