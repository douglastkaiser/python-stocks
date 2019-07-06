
from TradingHistory import TradingHistory
import numpy as np
from dougs_strategies import *
import matplotlib.pyplot as plt
import pandas as pd

def run_some_strategies(initial_deposit, historic_data):

    ticker_list = historic_data.tickers()
    ticker_list.append('bank_account')
    ticker_list.append('money_invested')

    th_list = []
    th_list.append(TradingHistory(ticker_list, initial_deposit, strategy_no_investment, 'None'))
    th_list.append(TradingHistory(ticker_list, initial_deposit, strategy_spy_asap_investment, 'SPY ASAP'))
    th_list.append(TradingHistory(ticker_list, initial_deposit, strategy_dia_asap_investment, 'DIA ASAP'))
    # th_list.append(TradingHistory(ticker_list, initial_deposit, strategy_ndaq_asap_investment, 'NDAQ ASAP'))
    # th_list.append(TradingHistory(ticker_list, initial_deposit, strategy_tqq_asap_investment, 'TQQ ASAP'))
    # th_list.append(TradingHistory(ticker_list, initial_deposit, strategy_maf_investment, 'MAF'))

    # Main loop through each day. #
    for row_n in range(1, historic_data.total_days()):
        stock_df_to_today, money_to_add = historic_data.get_stock_df_to_today_and_money_to_add(row_n)

        for th in th_list:
            th.new_day(stock_df_to_today, money_to_add)
    
    for th in th_list:
        th.add_port_value_to_plt()
        th.printer()

