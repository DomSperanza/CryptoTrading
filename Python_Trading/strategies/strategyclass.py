from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
import ta


class StrategyClass(ABC):
    """
    The Abstract Class defines a template method that contains a skeleton of
    some algorithm, composed of calls to (usually) abstract primitive
    operations.

    Concrete subclasses should implement these operations, but leave the
    template method itself intact.
    """
    trades_df: pd.DataFrame

    @abstractmethod
    def __init__(self) -> None:
        ...

    # common operations among all strategies
    def crossabove(self, fast: pd.DataFrame, slow: pd.DataFrame) -> pd.Series:
        series = pd.Series(np.where(fast > slow, 1, 0))
        series = series.diff()
        series = np.where(series == 1, 1, 0)
        return series

    def crossbelow(self, fast: pd.DataFrame, slow: pd.DataFrame) -> pd.Series:
        series = pd.Series(np.where(fast < slow, 1, 0))
        series = series.diff()
        series = np.where(series == 1, 1, 0)
        return series

    def get_trades_df(self, buydates, buyprice, selldates, sellprice):
        self.trades_df = pd.DataFrame([buydates, selldates, buyprice, sellprice]).T
        self.trades_df.columns = ['buydates', 'selldates', 'buyprices', 'sellprices']
        self.trades_df.dropna(inplace=True)
        self.trades_df['profit_rel'] = (self.trades_df.sellprices -
                                self.trades_df.buyprices)/self.trades_df.buyprices
        self.trades_df['cummulative_profit'] = (self.trades_df.profit_rel+1).cumprod()
        self.trades_df['profit_net'] = self.trades_df.profit_rel - 0.0015
        self.trades_df['cummulative_profit_fee'] = (self.trades_df.profit_net+1).cumprod()
        self.trades_df['profit_bool'] = np.where(self.trades_df.profit_rel > 0, True, False)
        self.trades_df['profit_bool_fee'] = np.where(
            self.trades_df.profit_net > 0, True, False)
        return self.trades_df

    # methods unique to each strategy
    @abstractmethod
    def apply_indicators(self) -> pd.DataFrame:
        '''Apply the indicators of the given strategy to the dataframe'''
        ...

    @abstractmethod
    def apply_strat(self) -> pd.DataFrame:
        '''Apply the given strategy to the dataframe'''
        ...

    # methods that may be overwritten by the strategy
    @abstractmethod
    def plot_visual(self):
        ...

    def buy_and_hold(self):
        buy = self.df.Close[1]
        sell =self.df.Close[-1]
        self.profit = ((sell-buy)/buy-0.0015)+1
        return self.profit

    def trades_stats(self):
        statsdict = {}
        statsdict['profit_no_fee'] = (self.trades_df.profit_rel+1).prod()
        statsdict['profit_fee'] = (self.trades_df.profit_net+1).prod()
        statsdict['winrate'] = self.trades_df.profit_bool.sum()/len(self.trades_df)
        statsdict['buyhold'] = self.buy_and_hold()
        return statsdict