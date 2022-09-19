from .strategyclass import StrategyClass
import pandas as pd
import numpy as np
import ta
import matplotlib.pyplot as plt

class HeikenStoch(StrategyClass):

    def __init__(self, df = pd.DataFrame, trades_df = pd.DataFrame) -> None:
        self.df = df
        self.trades_df = trades_df

    def apply_indicators(self) -> pd.Dataframe:
         # for plot purposes
        df['SMA_50'] = ta.trend.sma_indicator(df.Close, window=50)

        OpenH = [self.df.iloc[0].Open]*len(self.df)
        CloseH = 1/4*(self.df.Open+self.df.High+self.df.Low+self.df.Close)
        for i in range(1, len(self.df)):
            OpenH[i] = (CloseH[i-1]+OpenH[i-1])/2
        df['OpenH'] = OpenH
        df['HighH'] = self.df[['High', 'OpenH', 'Close']].max(axis=1)
        df['LowH'] = self.df[['Low', 'OpenH', 'Close']].min(axis=1)
        df['CloseH'] = CloseH

        # ema
        df['EMA_200'] = ta.trend.ema_indicator(df.CloseH, window=200)

        # stoch RSI
        # d is the orange line, k is the blue line in trading view
        df['stoch_k'] = ta.momentum.stochrsi_k(df.CloseH, window=14)
        df['stoch_d'] = ta.momentum.stochrsi_d(df.CloseH, window=14)
        df['rsi_crossover'] = crossabove(df.stoch_k, df.stoch_d)

    def apply_strat(self) -> pd.Dataframe:
        in_position = False
        buydates = []
        buyprice = []
        selldates = []
        sellprice = []

        for i in range(2, len(self.df)):
            if ~(in_position) & (i+1 < len(self.df)):
                if ((self.df.iloc[i].rsi_crossover == 1) &
                    ((self.df.iloc[i].stoch_k <= .2) |
                     (self.df.iloc[i].stoch_d <= .2)) &
                    (self.df.iloc[i].CloseH-self.df.iloc[i].OpenH > self.df.iloc[i-1].CloseH-self.df.iloc[i-1].OpenH) &
                    (self.df.iloc[i].CloseH > self.df.iloc[i].OpenH) &
                    (self.df.iloc[i-1].CloseH > self.df.iloc[i-1].OpenH) &
                        (self.df.iloc[i].CloseH >= self.df.iloc[i].EMA_200)):

                    buydates.append(self.df.iloc[i].name)
                    buyprice.append(self.df.iloc[i].Close)
                    SL = min(min(self.df[i-5:i].Low), self.df.iloc[i].Close*.995)
                    Risk = 1-(SL/self.df.iloc[i].Close)
                    TP = self.df.iloc[i].Close+self.df.iloc[i].Close*Risk*1.5

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

        trades_df = get_trades_df(buydates, buyprice, selldates, sellprice)
        return trades_df        


if __name__ == '__main__':
    pass