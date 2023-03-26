from turtle import rt
from .strategyclass import StrategyClass
import pandas as pd
import numpy as np
import ta
import math
import matplotlib.pyplot as plt

class Magic(StrategyClass):
    
    def __init__(self, df = pd.DataFrame, trades_df = pd.DataFrame) -> None:
        self.df = df
        self.trades_df = trades_df

    def apply_indicators(self) -> pd.DataFrame:
        # macd lines and crossover
        self.df['fastMA'] = ta.trend.ema_indicator(self.df.Close, 20)
        self.df['slowMA'] = ta.trend.ema_indicator(self.df.Close, 30)
        self.df['MACD'] = ta.trend.macd(self.df.Close, window_slow=30, window_fast=20)
        self.df['MACD_sig'] = ta.trend.sma_indicator(self.df.MACD, window=10)
        self.df['MACD_cross'] = self.crossabove(self.df.MACD, self.df.MACD_sig)

        #ADX and DI
        length = 14
        TR = ta.volatility.average_true_range(
            self.df.High, self.df.Low, self.df.Close, window=1)
        DMP = np.where((self.df.High-self.df.High.shift(1)) >
                       (self.df.Low.shift(1)-self.df.Low), self.df.High-self.df.High.shift(1), 0)
        DMP = np.where(DMP < 0, 0, DMP)
        DMM = np.where((self.df.Low.shift(1)-self.df.Low) >
                       (self.df.High-self.df.High.shift(1)), self.df.Low.shift(1)-self.df.Low, 0)
        DMM = np.where(DMM < 0, 0, DMM)
        STR = [0]*len(self.df)
        SDMP = [0]*len(self.df)
        SDMM = [0]*len(self.df)

        for i in range(1, len(self.df)):
            STR[i] = (STR[i-1]-STR[i-1]/length)+TR[i]
            SDMP[i] = (SDMP[i-1]-SDMP[i-1]/length)+DMP[i]
            SDMM[i] = (SDMM[i-1]-SDMM[i-1]/length)+DMM[i]
        SDMP = pd.Series(SDMP, index=self.df.index)
        SDMM = pd.Series(SDMM, index=self.df.index)
        STR = pd.Series(STR, index=self.df.index)
        DIPlus = SDMP/STR*100
        DIMinus = SDMM/STR*100
        DXtest = pd.Series(abs(DIPlus-DIMinus) /
                           (DIPlus+DIMinus)*100, index=self.df.index)
        self.df['ADX'] = ta.trend.sma_indicator(DXtest, length)

        # Bar colors indicator
        length = 200
        MGma = [0]*len(self.df)

        MGma[0] = self.df.iloc[0].Close
        for i in range(1, len(self.df)):
            MGma[i] = MGma[i-1]+(self.df.iloc[i].Close-MGma[i-1]) / \
                (length*(self.df.iloc[i].Close/MGma[i-1])**4)
        MGma = pd.Series(MGma, index=self.df.index)
        TR = pd.Series(ta.volatility.average_true_range(
            self.df.High, self.df.Low, self.df.Close, window=1))
        rangema = ta.trend.ema_indicator(TR, window=200)

        multy = 0.2

        upperk = MGma+rangema*multy
        lowerk = MGma-rangema*multy

        self.df['BarColor'] = np.where(self.df.Close > upperk, 'Blue', np.where(
            self.df.Close < lowerk, 'Red', 'Gray'))

    def apply_strat(self) -> pd.DataFrame:
        in_position = False
        buydates = []
        buyprice = []
        selldates = []
        sellprice = []   

        for i in range(200, len(self.df)):
            if ~(in_position) & (i+1 < len(self.df)):
                if (((self.df.iloc[i].BarColor == 'Blue') | (self.df.iloc[i].BarColor == 'Gray')) &
                    (self.df.iloc[i].ADX >= 20) &
                    (self.df.iloc[i].MACD_cross == 1) &
                        ((self.df.iloc[i].MACD > 0) | (self.df.iloc[i].MACD_sig > 0))):

                    buydates.append(self.df.iloc[i].name)
                    buyprice.append(self.df.iloc[i].Close)
                    SL = min(min(self.df[i-10:i].Low), self.df.iloc[i].Close*.9975)
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
                    
        trades_df = self.get_trades_df(buydates, buyprice, selldates, sellprice)
        return trades_df


if __name__ == '__main__':
    pass
    # strat  = Magic()