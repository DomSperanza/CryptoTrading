from turtle import rt
from .strategyclass import StrategyClass
import pandas as pd
import numpy as np
import ta
import math
import matplotlib.pyplot as plt

class Heiken_EMA(StrategyClass):
    
    def __init__(self, df = pd.DataFrame, trades_df = pd.DataFrame) -> None:
        self.df = df
        self.trades_df = trades_df

    def apply_indicators(self) -> pd.DataFrame:
        # heiken ashi candle sticks
        OpenH = [self.df.iloc[0].Open]*len(self.df)
        CloseH = 1/4*(self.df.Open+self.df.High+self.df.Low+self.df.Close)
        for i in range(1, len(self.df)):
            OpenH[i] = (CloseH[i-1]+OpenH[i-1])/2
        self.df['OpenH'] = OpenH
        self.df['HighH'] = self.df[['High', 'OpenH', 'Close']].max(axis=1)
        self.df['LowH'] = self.df[['Low', 'OpenH', 'Close']].min(axis=1)
        self.df['CloseH'] = CloseH
        self.df['ColorH'] = np.where(self.df.OpenH < self.df.CloseH, 'Green', 'Red')

        # emas
        self.df['EMA_9'] = ta.trend.ema_indicator(self.df.CloseH, window=9)
        self.df['EMA_18'] = ta.trend.ema_indicator(self.df.CloseH, window=18)
        self.df['EMA_crossover'] = self.crossabove(self.df.EMA_9, self.df.EMA_18)
        self.df['EMA_crossbelow'] = self.crossbelow(self.df.EMA_9, self.df.EMA_18)
        self.df['EMA_9_above'] = np.where(self.df.EMA_9 > self.df.EMA_18, 1, 0)

        # trading rule for indicator
        signal = [0]*len(self.df)
        counter = 0
        for i in range(1, len(self.df)):
            if (self.df.iloc[i].EMA_9_above == 1) & (self.df.iloc[i].LowH > self.df.iloc[i].EMA_9) & (self.df.iloc[i].OpenH < self.df.iloc[i].CloseH):
                counter = counter+1
                signal[i] = counter
            elif self.df.iloc[i].EMA_9_above == 0:
                counter = 0
        self.df['signal_count'] = signal
        self.df['good_signal'] = np.where(self.df.signal_count == 1, 1, 0)
        good_buy = [0]*len(self.df)
        js = [1]*len(self.df)
        ks = [1]*len(self.df)
        for i in range(1, len(self.df)):
            j = 1
            k = 1
            if i+2 >= len(self.df):
                break
            if self.df.iloc[i].good_signal == 1:
                while ((self.df.iloc[i+j].ColorH == 'Green') |
                       (self.df.iloc[i+j].LowH > self.df.iloc[i+j].EMA_9)):
                    j = j+1
                    if ((self.df.iloc[i+j].EMA_9_above == 0) |
                        (self.df.iloc[i+j].CloseH < self.df.iloc[i+j].EMA_18) |
                            (i+j+1 >= len(self.df))):
                        j = 0
                        break
                if (j > 0) & (self.df.iloc[i+j].CloseH > self.df.iloc[i+j].EMA_18) & (self.df.iloc[i+j].EMA_9_above == 1)&(i+j+k<len(self.df)):
                    while(((self.df.iloc[i+j+k].ColorH == 'Red') |
                          (self.df.iloc[i+j+k].CloseH < self.df.iloc[i+j+k].EMA_9))):
                        k = k+1
                        if (i+j+k>=len(self.df)):
                            break
                        if (self.df.iloc[i+j].EMA_9_above == 0) | (self.df.iloc[i+j].CloseH < self.df.iloc[i+j].EMA_18):
                            k = 0
                            j = 0
                            break
                    if (i+j+k>=len(self.df)):
                        break
                    if (j > 0) & (k > 0) & (self.df.iloc[i+j+k].EMA_9_above == 1):
                        good_buy[i+j+k] = 1

                    js[i] = j
                    ks[i] = k

        self.df['js'] = js
        self.df['ks'] = ks
        self.df['good_buy'] = good_buy

    def apply_strat(self) -> pd.DataFrame:
        in_position = False
        buydates = []
        buyprice = []
        selldates = []
        sellprice = []
        
        for i in range(1, len(self.df)):
            if ~(in_position) & (i+1 < len(self.df)):
                if (self.df.iloc[i].good_buy == 1):

                    buydates.append(self.df.iloc[i].name)
                    buyprice.append(self.df.iloc[i].Close)
                    SL = min(self.df.iloc[i-1].Low, self.df.iloc[i].Close*.998)
                    Risk = 1-(SL/self.df.iloc[i].Close)
                    TP = self.df.iloc[i].Close+self.df.iloc[i].Close*Risk*2

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
# heiken_ema