import numpy as np
import matplotlib.pyplot as plt

class TradingDay:

    def __init__(self, bank_account_history, shares_history, price_history):
        self.bank_account_history = bank_account_history
        self.shares_history = shares_history
        self.price_history = price_history

    #### GENERAL HELP ####
    def new_day(self, new_share_price, daily_investment):
        assert type(self) is TradingDay, "self is not of type TradingDay"

        self.bank_account_history.append(self.bank_account_history[-1] + daily_investment)
        self.shares_history.append(self.shares_history[-1])
        self.price_history.append(new_share_price)

        if self.bank_account_history[-1] < 0:
            self.sell_one_share()

    def current_protfolio_value(self):
        assert type(self) is TradingDay, "self is not of type TradingDay"

        current_value = self.bank_account_history[-1] + self.shares_history[-1]*self.price_history[-1]
        return current_value

    def portfolio_value_history(self):
        assert type(self) is TradingDay, "self is not of type TradingDay"

        value_history = []
        for i in range(0, len(self.bank_account_history)):
            value_history.append(self.bank_account_history[i] + self.shares_history[i]*self.price_history[i])
        return value_history

    #### BUY SELL HELP ####
    def buy_one_share(self):
        assert type(self) is TradingDay, "self is not of type TradingDay"

        if self.price_history[-1] < self.bank_account_history[-1]:
            self.shares_history[-1] += 1
            self.bank_account_history[-1] -= self.price_history[-1]

    def buy_all_shares(self):
        assert type(self) is TradingDay, "self is not of type TradingDay"

        shares_to_buy = int(self.bank_account_history[-1]/self.price_history[-1])
        self.bank_account_history[-1] -= shares_to_buy*self.price_history[-1]
        self.shares_history[-1] += shares_to_buy

    def sell_one_share(self):
        assert type(self) is TradingDay, "self is not of type TradingDay"

        if self.shares_history[-1] > 0:
            self.shares_history[-1] = self.shares_history[-1] - 1
            self.bank_account_history[-1] += self.price_history[-1]

    def sell_all_shares(self):
        assert type(self) is TradingDay, "self is not of type TradingDay"

        self.bank_account_history[-1] += self.shares_history[-1]*self.price_history[-1]
        self.shares_history[-1] = 0

    #### DISPLAY HELP ####
    def printer(self):
        assert type(self) is TradingDay, "self is not of type TradingDay"

        print("Shares Owned in end: " + str(self.shares_history[-1]))
        print("Bank Account left over: " + "%.2f" % self.bank_account_history[-1])
        protfolio_value = self.shares_history[-1]*self.price_history[-1] + self.bank_account_history[-1]
        print("Total Value: " + "%.2f" % protfolio_value)
        port_val_hist = self.portfolio_value_history()
        percentage_increase = (port_val_hist[-1] - port_val_hist[0])/port_val_hist[0]*100/10
        print("Total Percentage Increase: " + "%.2f" % percentage_increase + "%")

    def add_port_value_to_plt(self, label_for_legend):
        t = np.linspace(1, len(self.price_history), len(self.price_history))
        portfolio_value_history = self.portfolio_value_history()
        plt.plot(t, portfolio_value_history, label=label_for_legend)
