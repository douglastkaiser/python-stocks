
import numpy as np
import matplotlib.pyplot as plt
from math_helper import *
import pandas as pd
import math

class TradingHistory:

    def __init__(self, col_list, principal, strat_function, name):
        df = pd.DataFrame(columns=col_list)
        df.index = pd.to_datetime(df.index)

        self.trading_history_df = df
        self.principal = principal
        self.strat_function = strat_function
        self.stock_df_to_today = pd.DataFrame()
        self.name = name

    #### STRATS ####
    # def strat1(self):

    #### GENERAL HELP ####
    def new_day(self, stock_df_to_today, money_to_add):        
        self.stock_df_to_today = stock_df_to_today
        df = self.trading_history_df
        todays_date = stock_df_to_today.index[-1]
        # First day - add principal to bank account and init with zeros.
        if len(stock_df_to_today.index) <= 1:
            df.loc[todays_date] = [0]*len(df.columns)
            df['bank_account'][-1] = self.principal
        else:  # All other days - copy everything down.
            df.loc[todays_date] = df.iloc[-1]
        df['money_invested'][-1] = money_to_add
        df['bank_account'][-1] += df['money_invested'][-1]

        self.trading_history_df = df

        # Run that day's strategy.
        strat = self.strat_function
        self = strat(self)

    def current_protfolio_value(self, index):
        stock_value = 0
        for ticker in self.stock_df_to_today.columns.levels[0]:
            stock_prices = list(self.stock_df_to_today[ticker]['Close'])
            i = index
            while np.isnan(stock_prices[i]) and (i >= 0):
                i -= 1
            # Nothing found in history.
            if np.isnan(stock_prices[i]):
                valid_stock_price = 0
            else:
                valid_stock_price = stock_prices[i]
            stock_value += valid_stock_price*self.trading_history_df[ticker][index]
        return self.trading_history_df['bank_account'][index] + stock_value

    def portfolio_value_history(self):
        # Can vectorize?
        # Should return a Series object with timestamps.
        # apply function?
        value_history = []
        for i in range(0, len(self.trading_history_df.index)):
            value_history.append(self.current_protfolio_value(i))
        return value_history

    #### BUY SELL HELP ####
    # def buy_one_share(self):
    #     if self.price_history[-1] < self.bank_account_history[-1]:
    #         self.shares_history[-1] += 1
    #         self.bank_account_history[-1] -= self.price_history[-1]

    def buy_all_shares(self, ticker_name):
        ba = self.trading_history_df['bank_account'][-1]
        stock_price = self.stock_df_to_today[ticker_name]['Close'][-1]
        if not np.isnan(stock_price):
            shares_to_buy = int(ba/stock_price)
            self.trading_history_df['bank_account'][-1] -= shares_to_buy*stock_price
            self.trading_history_df[ticker_name][-1] += shares_to_buy

    # def sell_one_share(self):
    #     if self.shares_history[-1] > 0:
    #         self.shares_history[-1] = self.shares_history[-1] - 1
    #         self.bank_account_history[-1] += self.price_history[-1]

    def sell_all_shares(self, ticker_name):
        stock_price = self.stock_df_to_today[ticker_name]['Close'][-1]
        if (not np.isnan(stock_price)):
            shares_to_sell = self.trading_history_df[ticker_name][-1]
            self.trading_history_df['bank_account'][-1] += shares_to_sell*stock_price
            self.trading_history_df[ticker_name][-1] = 0

    def average_annual_percentage_change(self):
        # Can filter out whenever "money invested" is 0 from both Series.
        # https://www.fool.com/about/how-to-calculate-investment-returns/
        holding_period_return = 1
        port_val_hist = self.portfolio_value_history()
        money_added = self.trading_history_df['money_invested']
        total_money_add = money_added[0]
        for i in range(1, len(self.trading_history_df.index)):
            todays_change = port_val_hist[i]/(port_val_hist[i - 1] + money_added[i]) - 1
            holding_period_return = holding_period_return*(1 + todays_change)
        time_delta = self.trading_history_df.index[-1] - self.trading_history_df.index[0]
        time_weighted_return = holding_period_return - 1
        # return ((holding_period_return - 1)*100)^(365/time_delta.days)
        num_years = time_delta.days/365
        return ((time_weighted_return + 1)**(1/num_years) - 1)*100

    #### DISPLAY HELP ####
    def printer(self):
        print('\nStrat: ' + self.name + ":")
        for ticker in self.stock_df_to_today.columns.levels[0]:
            if self.trading_history_df[ticker][-1] is not 0:
                print("Shares of " + ticker + " Owned in the end: " + str(self.trading_history_df[ticker][-1]))
        print("Bank Account left over: " + "%.2f" % self.trading_history_df['bank_account'][-1])
        # protfolio_value = self.shares_history[-1]*self.price_history[-1] + self.bank_account_history[-1]
        port_val_hist = self.portfolio_value_history()
        print("Total Value: " + "%.2f" % port_val_hist[-1])

        percentage_increase = percentage_difference(port_val_hist[0], port_val_hist[-1])
        print("Total Percentage Increase: " + "%.2f" % percentage_increase + "%")
        ave_api = self.average_annual_percentage_change()
        print("HPR Annual Percentage Change: " + "%.2f" % ave_api + "%")

    def add_port_value_to_plt(self):
        portfolio_value_history = self.portfolio_value_history()
        plt.plot(self.trading_history_df.index, portfolio_value_history, label=self.name)
        plt.legend()
