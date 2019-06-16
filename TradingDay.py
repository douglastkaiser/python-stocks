class TradingDay:

    def __init__(self, bank_account_history, shares_history, price_history):
        self.bank_account_history = bank_account_history
        self.shares_history = shares_history
        self.price_history = price_history

    #### HELPERS
    def new_day(self, share_price, daily_investment):
        assert type(self) is TradingDay, "self is not of type TradingDay"

        self.bank_account_history.append(self.bank_account_history[-1] + daily_investment)
        self.shares_history.append(self.shares_history[-1])
        self.price_history.append(share_price)

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

    def printer(self):
        assert type(self) is TradingDay, "self is not of type TradingDay"

        print("Shares Owned in end: " + str(self.shares_history[-1]))
        print("Bank Account left over: " + "%.2f" % self.bank_account_history[-1])
        protfolio_value = self.shares_history[-1]*self.price_history[-1] + self.bank_account_history[-1]
        print("Total Value: " + "%.2f" % protfolio_value)
