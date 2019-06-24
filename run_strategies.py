
from TradingDay import TradingDay
import numpy as np
from dougs_strategies import *
import matplotlib.pyplot as plt

def run_some_strategies(initial_deposit, daily_investment, historic_data):
    print("Initial Deposit: " + str(initial_deposit))
    print("Daily Investment: " + str(daily_investment))

    ## Print full values
    fig = plt.figure()

    print("\n -- Strat = NONE --")
    no_investment_trading_day = run_strat_over_full_time(strategy_no_investment, historic_data, daily_investment, initial_deposit)
    no_investment_trading_day.add_port_value_to_plt('No Investment Strat')

    # print("\n -- Strat = MARCUS 2.25% --")
    # marcus_trading_day = run_strat_over_full_time(strategy_marcus_2p25, historic_data, daily_investment, initial_deposit)
    # marcus_trading_day.add_port_value_to_plt('MARCUS 2.25%')
    
    print("\n -- Strat = ASAP --")
    asap_investment_trading_day = run_strat_over_full_time(strategy_asap_investment, historic_data, daily_investment, initial_deposit)
    asap_investment_trading_day.add_port_value_to_plt('ASAP Strat')

    # print("\n -- Strat = SINUSOID --")
    # sinusoid_investment_trading_day = run_strat_over_full_time(strategy_sinusoid_investment, historic_data, daily_investment, initial_deposit)
    # sinusoid_investment_trading_day.add_port_value_to_plt('Sinusoid Strat')

    print("\n -- Strat = 100pt MAF --")
    maf_investment_trading_day = run_strat_over_full_time(strategy_maf_investment, historic_data, daily_investment, initial_deposit)
    maf_investment_trading_day.add_port_value_to_plt('MAF Strat')    
    
    plt.xlabel('Trading Days')
    plt.ylabel('Value ($)')
    plt.title("Portfolio Values for Different Strategies")
    plt.legend()


def run_strat_over_full_time(strat, historic_data, daily_investment, initial_deposit):

    close_prices = historic_data.closing_prices
    trading_day = TradingDay([initial_deposit], [0], [close_prices[0]])

    for i in range(0, len(close_prices)):
        trading_day.new_day(close_prices[i], daily_investment)
        trading_day = strat(trading_day)
    trading_day.printer()

    return trading_day
