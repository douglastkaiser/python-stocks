
import numpy as np
import pandas as pd

from .data_loading import load_into_stock_data_set
from .math_helper import no_delay_moving_average_filter_on_that_day_vectorized
from .plotting import plt

class StockData:

    def __init__(self, list_of_tickers, monthly_deposit=0, daily_deposit=0):
        data_frame_list=[]
        for ticker in list_of_tickers:
            data_frame_list.append(load_into_stock_data_set(ticker))
        df = pd.concat(data_frame_list, axis=1, keys=(list_of_tickers))
        # Reindex to fill missing days - non-trading days.
        inn = df.index
        idx = pd.date_range(inn[0], inn[-1])
        df = df.reindex(idx, fill_value=np.nan)
        self.data_frame = df
        self.monthly_deposit = monthly_deposit
        self.daily_deposit = daily_deposit

    def get_stock_df_to_today_and_money_to_add(self, row_n):
        # Create stock history df up to this day.
        stock_df_to_today = self.data_frame.iloc[:row_n]
        # Calculate the investment schedule.
        money_to_add = self.daily_deposit
        if stock_df_to_today.index[-1].day == 1:
            money_to_add += self.monthly_deposit
        return stock_df_to_today, money_to_add

    def add_external_investments(self, monthly_deposit, daily_deposit):
        self.monthly_deposit = monthly_deposit
        self.daily_deposit = daily_deposit

    def total_days(self):
        return len(self.data_frame.index)

    def tickers(self):
        return list(self.data_frame.columns.levels[0])

    def limit_timeframe(self, start_date, end_date):
        start = start_date or self.data_frame.index[0]
        end = end_date or self.data_frame.index[-1]
        self.data_frame = self.data_frame.loc[start:end]

    def plot(self):
        df = self.data_frame
        for ticker in self.tickers():
            plt.figure()
            sub_df = df[ticker]['Close']  # [['Close', 'Open', 'High', 'Low']]
            sub_df = sub_df[~sub_df.isin([np.nan, np.inf, -np.inf])]
            # sub_df.plot(kind='line', title=ticker+' Prices')
            data = list(sub_df)
            plt.plot(sub_df.index, data, label='Closing Prices')
            plt.plot(sub_df.index, no_delay_moving_average_filter_on_that_day_vectorized(data, 10), label='Closing Prices - on that day - MAF 10')
            plt.plot(sub_df.index, no_delay_moving_average_filter_on_that_day_vectorized(data, 100), label='Closing Prices - on that day - MAF 100')
            plt.legend()
            plt.title(ticker + ' Stock')

