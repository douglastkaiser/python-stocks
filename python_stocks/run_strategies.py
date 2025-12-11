
import matplotlib.pyplot as plt

from .dougs_strategies import (
    strategy_dia_asap_investment,
    strategy_maf_investment,
    strategy_marcus_2p25,
    strategy_ndaq_asap_investment,
    strategy_no_investment,
    strategy_openclose_investment,
    strategy_spy_asap_investment,
    strategy_tqq_asap_investment,
)
from .trading_history import TradingHistory

def run_some_strategies(initial_deposit, historic_data):

    ticker_list = historic_data.tickers()

    ticker_list.append('bank_account')
    ticker_list.append('money_invested')

    th_list = []
    th_list.append(TradingHistory(ticker_list, initial_deposit, strategy_no_investment, 'None'))
    th_list.append(TradingHistory(ticker_list, initial_deposit, strategy_spy_asap_investment, 'SPY asap'))
    # th_list.append(TradingHistory(ticker_list, initial_deposit, strategy_dia_asap_investment, 'DIA asap'))
    # th_list.append(TradingHistory(ticker_list, initial_deposit, strategy_ndaq_asap_investment, 'NDAQ asap'))
    # th_list.append(TradingHistory(ticker_list, initial_deposit, strategy_tqq_asap_investment, 'TQQ asap'))
    # th_list.append(TradingHistory(ticker_list, initial_deposit, strategy_marcus_2p25, 'Marcus 2.25%'))
    # th_list.append(TradingHistory(ticker_list, initial_deposit, strategy_maf_investment, 'MAF Strategy'))
    th_list.append(TradingHistory(ticker_list, initial_deposit, strategy_openclose_investment, 'Devangs OpenClose Strategy'))

    ##### Main loop through each day.
    for row_n in range(1, historic_data.total_days()):
        stock_df_to_today, money_to_add = historic_data.get_stock_df_to_today_and_money_to_add(row_n)
        for th in th_list:
            th.new_day(stock_df_to_today, money_to_add)

    ##### Print out data and plots for the TradingHistory objects.
    for th in th_list:
        th.add_port_value_to_plt()
        th.printer()
