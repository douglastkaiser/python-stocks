
from TradingDay import TradingDay
import numpy as np
from dougs_strategies import *
import matplotlib.pyplot as plt

def run_some_strategies(initial_deposit, daily_investment, historic_data):
    print("Initial Deposit: " + str(initial_deposit))
    print("Daily Investment: " + str(daily_investment))


    # Pass strat function name to run_strat_over_full_time()
    print("\n -- Strat = NONE --")
    no_investment_trading_day = run_strat_over_full_time(strategy_no_investment, historic_data, daily_investment, initial_deposit)
    
    print("\n -- Strat = MARCUS 2.25% --")
    marcus_trading_day = run_strat_over_full_time(strategy_marcus_2p25, historic_data, daily_investment, initial_deposit)

    print("\n -- Strat = ASAP --")
    asap_investment_trading_day = run_strat_over_full_time(strategy_asap_investment, historic_data, daily_investment, initial_deposit)

    print("\n -- Strat = SINUSOID --")
    sinusoid_investment_trading_day = run_strat_over_full_time(strategy_sinusoid_investment, historic_data, daily_investment, initial_deposit)

    print("\n -- Strat = 100pt MAF --")
    maf_investment_trading_day = run_strat_over_full_time(strategy_maf_investment, historic_data, daily_investment, initial_deposit)

    ## Print full values
    fig = plt.figure()  # an empty figure with no axes
    x = np.linspace(1, historic_data.total_days(), historic_data.total_days())

    no_investment_trading_day.add_port_value_to_plt('No Investment Strat')
    marcus_trading_day.add_port_value_to_plt('MARCUS 2.25%')
    asap_investment_trading_day.add_port_value_to_plt('ASAP Strat')
    sinusoid_investment_trading_day.add_port_value_to_plt('Sinusoid Strat')
    maf_investment_trading_day.add_port_value_to_plt('MAF Strat')

    plt.xlabel('Trading Days')
    plt.ylabel('Value ($)')
    plt.title("Portfolio Values for Different Strategies")
    plt.legend()

def run_strat_over_full_time(strat, historic_data, daily_investment, initial_deposit):

    close_prices = historic_data.closing_prices
    trading_day = TradingDay([initial_deposit], [0], [close_prices[0]])

    for i in range(1, len(close_prices)):
        trading_day.new_day(close_prices[i], daily_investment)
        trading_day = strat(trading_day)
    trading_day.printer()

    return trading_day
