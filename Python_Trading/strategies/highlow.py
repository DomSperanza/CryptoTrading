from .strategyclass import StrategyClass
import pandas as pd
import numpy as np
import ta
import matplotlib.pyplot as plt

class HighLow(StrategyClass):
    
    def __init__(self, df = pd.DataFrame, trades_df = pd.DataFrame) -> None:
        self.df = df
        self.trades_df = trades_df

    def apply_indicators(self) -> pd.DataFrame:
        # SMAs, also for plot purposes
        self.df['SMA_50'] = ta.trend.sma_indicator(self.df.Close, window=50)
        
        # rolling high low mid
        self.df['rollhigh'] = self.df.High.rolling(15).max()
        self.df['rolllow'] = self.df.Low.rolling(15).min()
        self.df['mid'] = (self.df.rollhigh+self.df.rolllow)/2
        self.df['highapproach'] = np.where(self.df.Close > self.df.rollhigh*0.999, 1, 0)
        self.df['close_a_mid'] = np.where(self.df.Close > self.df.mid, 1, 0)
        self.df['midcross'] = self.df.close_a_mid.diff() == 1
        return self.df

    def apply_strat(self) -> pd.DataFrame:
        in_position = False
        buydates = []
        buyprice = []
        selldates = []
        sellprice = []
        
        for i in range(len(self.df)):
            if ~(in_position) & (i+1 < len(self.df)):
                if ((self.df.iloc[i].midcross) &
                        (self.df.iloc[i].Close > self.df.iloc[i].SMA_50)):
                    buydates.append(self.df.iloc[i].name)
                    buyprice.append(self.df.iloc[i].Close)
                    TP = self.df.iloc[i].Close*1.02
                    SL = self.df.iloc[i].Close*.99
                    in_position = True
                    continue

            if (in_position) & (i+1 < len(self.df)):
                if (self.df.iloc[i].Low < SL):
                    sellprice.append(SL)
                    selldates.append(self.df.iloc[i].name)
                    in_position = False
                elif (self.df.iloc[i].High > TP):
                    sellprice.append(TP)
                    selldates.append(self.df.iloc[i].name)
                    in_position = False

        self.trades_df = self.get_trades_df(buydates, buyprice, selldates, sellprice)
        return self.trades_df
        

if __name__ == '__main__':
    pass
    # import example_df
    # strat  = HighLow()