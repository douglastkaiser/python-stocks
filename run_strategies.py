
from TradingDay import TradingDay
import numpy as np
from dougs_strategies import *
import matplotlib.pyplot as plt

def run_some_strategies(initial_deposit, daily_investment, close_prices):
    print("Initial Deposit: " + str(initial_deposit))
    print("Daily Investment: " + str(daily_investment))

    # Pass strat function name to run_strat_over_full_time()
    print("\n -- Strat = NONE --")
    strategy_no_investment_trading_day = run_strat_over_full_time(strategy_no_investment, close_prices, daily_investment, initial_deposit)
    strategy_no_investment_trading_day.printer()

    print("\n -- Strat = ASAP --")
    strategy_asap_investment_trading_day = run_strat_over_full_time(strategy_asap_investment, close_prices, daily_investment, initial_deposit)
    strategy_asap_investment_trading_day.printer()

    print("\n -- Strat = SINUSOID --")
    strategy_sinusoid_investment_trading_day = run_strat_over_full_time(strategy_sinusoid_investment, close_prices, daily_investment, initial_deposit)
    strategy_sinusoid_investment_trading_day.printer()

    print("\n -- Strat = 100pt MAF --")
    strategy_maf_investment_trading_day = run_strat_over_full_time(strategy_maf_investment, close_prices, daily_investment, initial_deposit)
    strategy_maf_investment_trading_day.printer()


    ## Print full values
    fig = plt.figure()  # an empty figure with no axes
    x = np.linspace(1, len(close_prices), len(close_prices))

    strategy_no_investment_trading_day.add_port_value_to_plt('No Investment Strat')
    strategy_asap_investment_trading_day.add_port_value_to_plt('ASAP Strat')
    strategy_sinusoid_investment_trading_day.add_port_value_to_plt('Sinusoid Strat')
    strategy_maf_investment_trading_day.add_port_value_to_plt('MAF Strat')

    plt.xlabel('Trading Days')
    plt.ylabel('Value ($)')
    plt.title("Portfolio Values for Different Strategies")
    plt.legend()

def run_strat_over_full_time(strat, close_prices, daily_investment, initial_deposit):

    trading_day = TradingDay([initial_deposit], [0], [close_prices[0]])

    for i in range(1, len(close_prices)):
        trading_day.new_day(close_prices[i], daily_investment)
        trading_day = strat(trading_day)

    return trading_day
