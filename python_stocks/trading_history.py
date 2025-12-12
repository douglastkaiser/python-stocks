
import numpy as np
import pandas as pd

from .math_helper import percentage_difference
from .plotting import plt

class TradingHistory:

    def __init__(
        self,
        col_list,
        principal,
        strat_function,
        name,
        *,
        transaction_cost_rate: float = 0.0,
        slippage_pct: float = 0.0,
    ):
        df = pd.DataFrame(columns=col_list)
        df.index = pd.to_datetime(df.index)

        self.trading_history_df = df
        self.principal = principal
        self.strat_function = strat_function
        self.stock_df_to_today = pd.DataFrame()
        self.name = name
        self.transaction_cost_rate = max(0.0, transaction_cost_rate)
        self.slippage_pct = max(0.0, slippage_pct)
        self.total_fees: float = 0.0
        self.total_slippage_cost: float = 0.0

    #### STRATS ####
    # def strat1(self):

    #### GENERAL HELP ####
    def new_day(self, stock_df_to_today, money_to_add):
        self.stock_df_to_today = stock_df_to_today
        df = self.trading_history_df
        todays_date = stock_df_to_today.index[-1]

        is_first_day = len(stock_df_to_today.index) <= 1
        if is_first_day:
            df.loc[todays_date] = [0] * len(df.columns)
            starting_bank = 0
        else:
            df.loc[todays_date] = df.iloc[-1]
            starting_bank = df.at[todays_date, "bank_account"]

        deposit = money_to_add + (self.principal if is_first_day else 0)
        df.at[todays_date, "money_invested"] = deposit
        df.at[todays_date, "bank_account"] = starting_bank + deposit

        self.trading_history_df = df

        strat = self.strat_function
        self = strat(self)

    def _get_effective_price(self, ticker: str, column: str, index: int) -> float | None:
        prices = self.stock_df_to_today[ticker][column]
        if index >= len(prices):
            return None

        valid_history = prices.iloc[: index + 1].dropna()
        if valid_history.empty:
            return None
        return float(valid_history.iloc[-1])

    def _price_with_slippage(self, base_price: float, is_buy: bool) -> float:
        if is_buy:
            return base_price * (1 + self.slippage_pct)
        return base_price * (1 - self.slippage_pct)

    def current_portfolio_value(self, index):
        stock_value = 0
        for ticker in self.stock_df_to_today.columns.levels[0]:
            valid_stock_price = self._get_effective_price(ticker, "Close", index)
            if valid_stock_price is None:
                continue
            stock_value += valid_stock_price * self.trading_history_df.at[self.trading_history_df.index[index], ticker]
        return self.trading_history_df.at[self.trading_history_df.index[index], "bank_account"] + stock_value

    def current_protfolio_value(self, index):
        return self.current_portfolio_value(index)

    def portfolio_value_history(self):
        # Can vectorize?
        # Should return a Series object with timestamps.
        # apply function?
        value_history = []
        for i in range(0, len(self.trading_history_df.index)):
            value_history.append(self.current_portfolio_value(i))
        return value_history

    #### BUY SELL HELP ####
    # def buy_one_share(self):
    #     if self.price_history[-1] < self.bank_account_history[-1]:
    #         self.shares_history[-1] += 1
    #         self.bank_account_history[-1] -= self.price_history[-1]

    def buy_all_shares(self, ticker_name, whentobuy='Close'):
        latest_index = len(self.trading_history_df.index) - 1
        bank_account = self.trading_history_df.at[self.trading_history_df.index[-1], "bank_account"]
        base_price = self._get_effective_price(ticker_name, whentobuy, latest_index)
        if base_price is None or bank_account <= 0:
            return

        stock_price = self._price_with_slippage(base_price, True)
        total_per_share = stock_price * (1 + self.transaction_cost_rate)
        shares_to_buy = int(bank_account / total_per_share)
        if shares_to_buy <= 0:
            return

        trade_value = shares_to_buy * stock_price
        transaction_cost = trade_value * self.transaction_cost_rate
        slippage_cost = shares_to_buy * (stock_price - base_price)
        updated_bank = bank_account - trade_value - transaction_cost
        updated_position = self.trading_history_df.at[self.trading_history_df.index[-1], ticker_name] + shares_to_buy

        self.trading_history_df.at[self.trading_history_df.index[-1], "bank_account"] = max(0.0, updated_bank)
        self.trading_history_df.at[self.trading_history_df.index[-1], ticker_name] = updated_position
        self.total_fees += transaction_cost
        self.total_slippage_cost += max(0.0, slippage_cost)

    # def sell_one_share(self):
    #     if self.shares_history[-1] > 0:
    #         self.shares_history[-1] = self.shares_history[-1] - 1
    #         self.bank_account_history[-1] += self.price_history[-1]

    def sell_all_shares(self, ticker_name, whentobuy='Close'):
        latest_index = len(self.trading_history_df.index) - 1
        shares_to_sell = self.trading_history_df.at[self.trading_history_df.index[-1], ticker_name]
        if shares_to_sell <= 0:
            return

        base_price = self._get_effective_price(ticker_name, whentobuy, latest_index)
        if base_price is None:
            return

        stock_price = self._price_with_slippage(base_price, False)
        trade_value = shares_to_sell * stock_price
        transaction_cost = trade_value * self.transaction_cost_rate
        slippage_cost = shares_to_sell * (base_price - stock_price)
        updated_bank = self.trading_history_df.at[self.trading_history_df.index[-1], "bank_account"] + trade_value - transaction_cost

        self.trading_history_df.at[self.trading_history_df.index[-1], "bank_account"] = max(0.0, updated_bank)
        self.trading_history_df.at[self.trading_history_df.index[-1], ticker_name] = 0
        self.total_fees += transaction_cost
        self.total_slippage_cost += max(0.0, slippage_cost)

    def time_weighted_return(self, annualize: bool = True):
        holding_period_return = 1
        port_val_hist = self.portfolio_value_history()
        money_added = self.trading_history_df["money_invested"].fillna(0)
        for i in range(1, len(self.trading_history_df.index)):
            todays_change = port_val_hist[i] / (port_val_hist[i - 1] + money_added.iloc[i]) - 1
            holding_period_return *= 1 + todays_change

        time_delta = self.trading_history_df.index[-1] - self.trading_history_df.index[0]
        time_weighted_return = holding_period_return - 1
        if not annualize or time_delta.days <= 0:
            return time_weighted_return

        num_years = time_delta.days / 365
        return (1 + time_weighted_return) ** (1 / num_years) - 1

    def money_weighted_return(self, annualize: bool = True):
        port_val_hist = self.portfolio_value_history()
        money_added = self.trading_history_df["money_invested"].fillna(0)

        cash_flows = [-float(money) for money in money_added]
        cash_flows.append(port_val_hist[-1])

        irr = self._internal_irr(cash_flows)
        if irr is None or not np.isfinite(irr):
            return 0

        time_delta = self.trading_history_df.index[-1] - self.trading_history_df.index[0]
        if not annualize or time_delta.days <= 0:
            return irr

        num_years = time_delta.days / 365
        return (1 + irr) ** (1 / num_years) - 1

    def _internal_irr(self, cash_flows: list[float], *, guess: float = 0.1) -> float:
        rate = guess
        for _ in range(100):
            npv = sum(cf / (1 + rate) ** i for i, cf in enumerate(cash_flows))
            derivative = sum(-i * cf / (1 + rate) ** (i + 1) for i, cf in enumerate(cash_flows))
            if abs(derivative) < 1e-12:
                break

            new_rate = rate - npv / derivative
            if not np.isfinite(new_rate):
                break
            if abs(new_rate - rate) < 1e-6:
                return new_rate
            rate = new_rate

        return rate

    def drawdown_series(self):
        portfolio_values = pd.Series(self.portfolio_value_history(), index=self.trading_history_df.index)
        if portfolio_values.empty:
            return pd.Series(dtype=float)
        running_max = portfolio_values.cummax()
        return portfolio_values / running_max - 1

    #### DISPLAY HELP ####
    def printer(self):
        print('\nStrat: ' + self.name + ":")
        for ticker in self.stock_df_to_today.columns.levels[0]:
            if self.trading_history_df[ticker][-1] != 0:
                print("Shares of " + ticker + " Owned in the end: " + str(self.trading_history_df[ticker][-1]))
        print("Bank Account left over: " + "%.2f" % self.trading_history_df['bank_account'][-1])
        # protfolio_value = self.shares_history[-1]*self.price_history[-1] + self.bank_account_history[-1]
        port_val_hist = self.portfolio_value_history()
        print("Total Value: " + "%.2f" % port_val_hist[-1])

        percentage_increase = percentage_difference(port_val_hist[0], port_val_hist[-1])
        print("Total Percentage Increase: " + "%.2f" % percentage_increase + "%")
        twr = self.time_weighted_return()
        mwr = self.money_weighted_return()
        drawdown = self.drawdown_series()
        print("Time-Weighted Return (annualized): " + "%.2f" % (twr * 100) + "%")
        print("Money-Weighted Return (annualized): " + "%.2f" % (mwr * 100) + "%")
        if not drawdown.empty:
            print("Max Drawdown: " + "%.2f" % (drawdown.min() * 100) + "%")

    def add_port_value_to_plt(self):
        portfolio_value_history = self.portfolio_value_history()
        plt.plot(self.trading_history_df.index, portfolio_value_history, label=self.name)
        plt.legend()
