class TradingDay:

    def __init__(self, shares_owned, bank_account, price_history):
        self.shares_owned = shares_owned
        self.bank_account = bank_account
        self.price_history = price_history

    #### HELPERS
    def buy_one_share(self):
        assert type(self) is TradingDay, "self is not TradingDay"

        if self.price_history[-1] < self.bank_account:
            self.shares_owned += 1
            self.bank_account -= self.price_history[-1]

    def buy_all_shares(self):
        assert type(self) is TradingDay, "self is not TradingDay"

        shares_to_buy = int(self.bank_account/self.price_history[-1])
        self.bank_account -= shares_to_buy*self.price_history[-1]
        self.shares_owned += shares_to_buy

    def sell_one_share(self):
        assert type(self) is TradingDay, "self is not TradingDay"

        if self.shares_owned > 0:
            self.shares_owned = self.shares_owned - 1
            self.bank_account += self.price_history[-1]

    def sell_all_shares(self):
        assert type(self) is TradingDay, "self is not TradingDay"

        self.bank_account += self.shares_owned*self.price_history[-1]
        self.shares_owned = 0

    def printer(self):
        assert type(self) is TradingDay, "self is not TradingDay"

        print("Shares Owned in end: " + str(self.shares_owned))
        print("Bank Account left over: " + "%.2f" % self.bank_account)
        protfolio_value = self.shares_owned*self.price_history[-1] + self.bank_account
        print("Total Value: " + "%.2f" % protfolio_value)
