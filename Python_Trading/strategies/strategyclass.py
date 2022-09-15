from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
import ta
import matplotlib.pyplot as plt


class StrategyClass(ABC):
    """
    The Abstract Class defines a template method that contains a skeleton of
    some algorithm, composed of calls to (usually) abstract primitive
    operations.

    Concrete subclasses should implement these operations, but leave the
    template method itself intact.
    """

    @abstractmethod
    def __init__(self, df: pd.DataFrame) -> None:
        self.trades_df = None
        ...

    # def template_method(self) -> None:
    #     """
    #     The template method defines the skeleton of an algorithm.
    #     """
    #     self.crossabove()
    #     self.crossbelow()
    #     self.applyindicators()
    #     self.hook2()

    # These operations already have implementations.
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

    # These operations have to be implemented in subclasses.
    @abstractmethod
    def apply_indicators(self) -> pd.DataFrame:
        '''Apply the indicators of the given strategy to the dataframe'''
        ...

    @abstractmethod
    def apply_strat(self) -> pd.DataFrame:
        '''Apply the given strategy to the dataframe'''
        ...

    def plot_visual(self):

        plt.style.use('dark_background')
        plt.figure(figsize=(20, 10))
        plt.title(self.symbol)
        plt.plot(self.df[['SMA_50']])
        plt.scatter(self.tradesdf.buydates, self.tradesdf.buyprices,
                    marker='^', color='g', s=200)
        plt.scatter(self.tradesdf.selldates, self.tradesdf.sellprices,
                    marker='v', color='r', s=200)
        plt.grid()
        plt.show()

    def buy_and_hold(self):
        buy = self.df.Close[1]
        sell =self.df.Close[-1]
        profit = ((sell-buy)/buy-0.0015)+1
        return profit

    def trades_stats(self):
        statsdict = {}
        statsdict['profit_no_fee'] = (self.tradesdf.profit_rel+1).prod()
        statsdict['profit_fee'] = (self.tradesdf.profit_net+1).prod()
        statsdict['winrate'] = self.tradesdf.profit_bool.sum()/len(self.tradesdf)
        statsdict['buyhold'] = self.buy_and_hold(self.df)
        return statsdict
