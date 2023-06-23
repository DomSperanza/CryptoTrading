#from turtle import rt
from .strategyclass import StrategyClass
import pandas as pd
import numpy as np
import ta
import math
import matplotlib.pyplot as plt

class Lazy_Bear(StrategyClass):
    
    def __init__(self, df = pd.DataFrame, trades_df = pd.DataFrame) -> None:
        self.df = df
        self.trades_df = trades_df

    def apply_indicators(self) -> pd.DataFrame:
        #Rules for trade:
            ## must be green coral trend (positive slope)
            ## must close above (start looking)
            ## must close below green coral trend
            ## must close aove the green line = Buy
            ## ADX: blue>20 and positive slope
            ## Green line above Red Line
            ## stoploss at recent swing low, target 1.5 times risk
        
        #Code up the Coral Trend indicator
        sm = 25
        cd = .4
        di = (sm-1)/2+1
        c1 = 2/(di+1)
        c2 = 1-c1
        c3 = 3 *(cd*cd+cd*cd*cd)
        c4 = -3*(2*cd**2+cd+cd**3)
        c5 = 3 *cd+1+cd**3+3*cd**2
        i_dict = {'i1':[],'i2':[],'i3':[],'i4':[],'i5':[],'i6':[]}
        i_dict['i1'].append(self.df.Close[0])
        i_list = list(i_dict.keys())
        #count=0
        for i_key in range(len(i_dict)):
            if i_key == 0:
                for ii in range(1,len(self.df)):
                    i_dict['i1'].append(c1*self.df.Close[ii]+c2*i_dict['i1'][ii-1])
            else:
                i_dict[i_list[i_key]].append(self.df.Close[0])
                for ii in range(1,len(self.df)):
                    i_dict[i_list[i_key]].append(c1*i_dict[i_list[i_key-1]][ii]+c2*i_dict[i_list[i_key]][ii-1])        
        self.df['bfr'] = -cd**3*np.array(i_dict['i6'])+c3*np.array(i_dict['i5'])+c4*np.array(i_dict['i4'])+c5*np.array(i_dict['i3'])
        bfrC = []
        bfrC.append('red')
        for jj in range(1,len(self.df)):
            if self.df.bfr[jj]>=self.df.bfr[jj-1]:
                bfrC.append('green')
            else:
                bfrC.append('red')
        self.df['bfrC'] = bfrC
        
        #pull back strat with the colors and price action
        Close_above = np.where(self.df.Close>self.df.bfr,1,0)
        cross_bfr = pd.Series(Close_above).diff()
        self.df['signal']=np.where(cross_bfr==1,1,0)
        
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
        self.df['DIPlus'] = DIPlus
        self.df['DIMinus'] = DIMinus

    def apply_strat(self) -> pd.DataFrame:
        in_position = False
        buydates = []
        buyprice = []
        selldates = []
        sellprice = []   

        for i in range(4, len(self.df)):
            if ~(in_position) & (i+1 < len(self.df)):
                if ((self.df.iloc[i].bfrC=='green')&
                    (self.df.iloc[i].signal ==1)&
                    (self.df.iloc[i].DIPlus>self.df.iloc[i].DIMinus)&
                    (self.df.iloc[i].ADX>15)):

                    buydates.append(self.df.iloc[i].name)
                    buyprice.append(self.df.iloc[i].Close)
                    SL = min(min(self.df[i-5:i].Low)*.999, self.df.iloc[i].Close*.995)
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
    # strat  = Lazy_Bear
