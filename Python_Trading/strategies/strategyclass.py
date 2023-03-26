from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
import ta
import matplotlib.pyplot as plt
import plotly.express as px


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
    def plot_visual(self):
        plt.style.use('dark_background')
        plt.figure(figsize=(20, 10))
        plt.title(self.symbol)
        plt.plot(self.df[['SMA_50']])
        plt.scatter(self.trades_df.buydates, self.trades_df.buyprices,
                    marker='^', color='g', s=200)
        plt.scatter(self.trades_df.selldates, self.trades_df.sellprices,
                    marker='v', color='r', s=200)
        plt.grid()
        plt.show()
        
    def plot_visual_plotly(self):
        fig = px.line(self.df, x=self.df.index, y='SMA_50', title=self.symbol)
        fig.add_scatter(x=self.trades_df.buydates, y=self.trades_df.buyprices, mode='markers',
                marker=dict(symbol='triangle-up', size=10, color='green'))
        fig.add_scatter(x=self.trades_df.selldates, y=self.trades_df.sellprices, mode='markers',
                marker=dict(symbol='triangle-down', size=10, color='red'))
        fig.update_layout(plot_bgcolor='black', paper_bgcolor='black',
                  xaxis=dict(title='Date'), yaxis=dict(title='Price'))
        fig.show()

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
