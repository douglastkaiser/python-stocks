
from TradingDay import TradingDay
import matplotlib.pyplot as plt
import numpy as np
from dougs_strategies import *

def run_some_strategies(initial_deposit, daily_investment, close_prices):
    print("Initial Deposit: " + str(initial_deposit))
    print("Daily Investment: " + str(daily_investment))

    # fig = plt.figure()  # an empty figure with no axes
    # fig.suptitle('No axes on this figure')  # Add a title so we know which it is
    # x = np.linspace(0, 2, len(close_prices))

    # plt.plot(x, close_prices, label='Closing Prices')
    # plt.xlabel('x label')
    # plt.ylabel('y label')
    # plt.title("Simple Plot")
    # plt.legend()
    # plt.show()

    print("\n -- Strat = NONE --")
    strategy_no_investment_trading_day = run_strat_over_time(strategy_no_investment, close_prices, daily_investment, initial_deposit)
    strategy_no_investment_trading_day.printer()

    print("\n -- Strat = ASAP --")
    strategy_asap_investment_trading_day = run_strat_over_time(strategy_asap_investment, close_prices, daily_investment, initial_deposit)
    strategy_asap_investment_trading_day.printer()

    print("\n -- Strat = SINUSOID --")
    strategy_sinusoid_investment_trading_day = run_strat_over_time(strategy_sinusoid_investment, close_prices, daily_investment, initial_deposit)
    strategy_sinusoid_investment_trading_day.printer()

    print("\n -- Strat = 100pt MAF --")
    strategy_maf_investment_trading_day = run_strat_over_time(strategy_maf_investment, close_prices, daily_investment, initial_deposit)
    strategy_maf_investment_trading_day.printer()

def run_strat_over_time(strat, close_prices, daily_investment, initial_deposit):

    trading_day = TradingDay([initial_deposit], [0], [close_prices[0]])

    for i in range(1, len(close_prices)):
        trading_day.new_day(close_prices[i], daily_investment)
        trading_day = strat(trading_day)

    return trading_day