from turtle import rt
from .strategyclass import StrategyClass
import pandas as pd
import numpy as np
import ta
import math
import matplotlib.pyplot as plt

class Boom(StrategyClass):
    
    def __init__(self, df = pd.DataFrame, trades_df = pd.DataFrame) -> None:
        self.df = df
        self.trades_df = trades_df

    def apply_indicators(self) -> pd.DataFrame:
        # for plot purposes
        self.df['SMA_50'] = ta.trend.sma_indicator(self.df.Close, window=50)

        # Hull moving average indicator
        self.df['WMA_200'] = ta.trend.wma_indicator(self.df.Close, window=200)
        self.df['HMA_200'] = ta.trend.wma_indicator(2*ta.trend.wma_indicator(self.df.Close, window=round(
            400/2))-ta.trend.wma_indicator(self.df.Close, window=400), window=round(math.sqrt(400)))
        self.df['Hull_color'] = np.where(
            self.df.HMA_200 > self.df.HMA_200.shift(2), 'green', 'red')

        # boom indicator (from YouTube)

        # make for loop go faster by making lists instead of appending a dataframe
        HP2 = [0]*len(self.df)
        LPP2 = 27
        alpha1222 = (math.cos(.707 * 2 * math.pi / 100) + math.sin(.707 *
                     2 * math.pi / 100) - 1) / math.cos(.707 * 2 * math.pi / 100)
        K22 = .3
        a12 = math.exp(-math.sqrt(2)*math.pi/LPP2)
        b12 = 2*a12*math.cos(math.sqrt(2)*math.pi/LPP2)
        c22 = b12
        c32 = -a12*a12
        c12 = 1-c22-c32
        esize = 60
        ey = 50

        LPP = 6
        K1 = 0
        a1 = math.exp(-math.sqrt(2)*math.pi/LPP)
        b1 = 2*a1*math.cos(math.sqrt(2)*math.pi/LPP)
        c2 = b1
        c3 = -a1*a1
        c1 = 1-c2-c3

        for i in range(2, len(self.df)):
            number = (1-alpha1222/2)**2*(self.df.iloc[i].Close-2*self.df.iloc[i-1].Close+self.df.iloc[i-2].Close) + 2*(
                1-alpha1222)*HP2[i-1] - (1-alpha1222)**2 * HP2[i-2]
            HP2[i] = number

        HP = HP2
        Filt = [0]*len(self.df)
        Filt2 = [0]*len(self.df)
        Peak = [0]*len(self.df)
        Peak2 = [0]*len(self.df)

        for i in range(2, len(self.df)):
            Filt[i] = c1*(HP[i]+HP[i-1])/2+c2*Filt[i-1]+c3*Filt[i-2]
            Peak[i] = .991*Peak[i-1]
            if abs(Filt[i]) > Peak[i]:
                Peak[i] = abs(Filt[i])

            Filt2[i] = c12*(HP2[i]+HP2[i-1])/2+c22*Filt2[i-1]+c32*Filt2[i-2]
            Peak2[i] = .991*Peak2[i-1]
            if abs(Filt2[i]) > Peak2[i]:
                Peak2[i] = abs(Filt2[i])

        df_boom = pd.DataFrame([Filt, Filt2, Peak, Peak2]).T
        df_boom.columns = ['Filt', 'Filt2', 'Peak', 'Peak2']
        X2 = np.where(df_boom.Peak2 != 0, df_boom.Filt2/df_boom.Peak2, 0)
        self.df['Q2'] = (X2+K22)/(K22*X2+1)*esize+ey
        X1 = np.where(df_boom.Peak != 0, df_boom.Filt/df_boom.Peak, 0)
        self.df['Q1'] = (X1+K1)/(K1*X1+1)*esize+ey
        self.df['Q_trigger'] = ta.trend.sma_indicator(self.df.Q1, window=2)
        self.df['cross_above_QT_Q2'] = self.crossabove(self.df.Q_trigger, self.df.Q2)

        # Volatility oscillator with relation to the std
        self.df['Vol_spike'] = self.df.Close-self.df.Open
        self.df['up_stdev'] = self.df.Vol_spike.rolling(100).std()
        return self.df

    def apply_strat(self) -> pd.DataFrame:
        in_position = False
        buydates = []
        buyprice = []
        selldates = []
        sellprice = []   

        for i in range(2, len(self.df)):
            if ~(in_position) & (i+1 < len(self.df)):
                if ((self.df.iloc[i].Q_trigger >= self.df.iloc[i].Q2) &
                    (self.df.iloc[i].cross_above_QT_Q2 == 1) &
                    (self.df.iloc[i].Close > self.df.iloc[i].HMA_200) &
                    (self.df.iloc[i].Hull_color == 'green') &
                        (max(self.df[i-1:i].Vol_spike) > self.df.iloc[i].up_stdev)):
                    buydates.append(self.df.iloc[i].name)
                    buyprice.append(self.df.iloc[i].Close)
                    SL = min(self.df[i-30:i].Low)*.998
                    Risk = 1-(SL/self.df.iloc[i].Close)
                    TP = self.df.iloc[i].Close+self.df.iloc[i].Close*Risk*2
                    #TSL = SL

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
        trades_df = self.get_trades_df(buydates, buyprice, selldates, sellprice)
        return trades_df


if __name__ == '__main__':
    pass
    # strat  = Boom()