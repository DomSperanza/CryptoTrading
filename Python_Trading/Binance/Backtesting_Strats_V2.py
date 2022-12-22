# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 13:21:41 2022

@author: dvspe
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Jun 24 18:28:11 2022

@author: dvspe
Purpose:
    Make an easily editable backtesting script that will allow me to see the effectiveness
    of trading strategies before implementing them. All functions and variables 
    can live in this script and binance functions can be ported over
    
    Going to be using methods similar to Algovibes from youtube to backtest

    Franco has been turning this into something more object orientated. Ill take a class on OOP and probably move away from thisstyle
    
Packages needed: ta, python-binance, pandas, numpy, etc
"""

# %% Import Packages needed

# should work ony any computer
#These imports included a lot of trial and error packages. Many are still  not used
import ta
import pandas as pd
import numpy as np
import os
from binance.client import Client
from scipy.stats import zscore
import matplotlib.pyplot as plt
from finta import TA as ta2
import math
path, filename = os.path.split(os.path.realpath(__file__))
# should got to Python_Trading AKA one directory up from current file's directory
os.chdir(path+"\..")



# %% Set up the Client from binance to get the data. No key needed
client = Client()


# %% Keep all functions here  with labels as to what they do.
def getdata(symbol, interval='1m', lookback='400', client=client):
    '''
    pulls data from Binance client looking back until present time
    
    Inputs: symbol(str),interval(str'1m',lookback(str) In Hours:'400',Client = client)

    Returns: Dataframe with candelstick data for specfied lookback to present. 
    '''
    frame = pd.DataFrame(client.get_historical_klines(symbol,
                                                      interval,
                                                      lookback + ' hours ago UTC'))
    frame = frame.iloc[:, 0:6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame.set_index('Time', inplace=True)
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame

# Checks to see if there is a crossover of the signal line


def crossabove(fast, slow):
       #Checks to see if the one line crosses above another line
    #Fast goes above slow
    series = pd.Series(np.where(fast > slow, 1, 0))
    series = series.diff()
    series = np.where(series == 1, 1, 0)
    return series


def crossbelow(fast, slow):
       #checks to see if one line crosses below another line
    #fast goes below slow
    series = pd.Series(np.where(fast < slow, 1, 0))
    series = series.diff()
    series = np.where(series == 1, 1, 0)
    return series


# define all the indicators needed for the strat testing
def applyindicators(df, strat):
    '''
    Purpose: Make new columns in the Dataframe based on the existing columns
    - This is whereindicators are developed from looking at pine script and converting to Python
    - These should be the exact same as the Backtesting.py scrip indicators
    
    Input:df: dataframe with Time, High, Low, Open,Close, and Volume Data
    strat(str): string of which strategy you are using

    Return: Original DataFrame With technical indicators so we can mimic strat online. 
    '''
    
    # for plot purposes
    df['SMA_50'] = ta.trend.sma_indicator(df.Close, window=50)

    if strat == 'High_Low':
        # SMAs
        df['SMA_50'] = ta.trend.sma_indicator(df.Close, window=50)
        # rolling high low mid
        df['rollhigh'] = df.High.rolling(15).max()
        df['rolllow'] = df.Low.rolling(15).min()
        df['mid'] = (df.rollhigh+df.rolllow)/2
        df['highapproach'] = np.where(df.Close > df.rollhigh*0.999, 1, 0)
        df['close_a_mid'] = np.where(df.Close > df.mid, 1, 0)
        df['midcross'] = df.close_a_mid.diff() == 1

    if strat == 'Boom':
        # Hull moving average indicator
        df['WMA_200'] = ta.trend.wma_indicator(df.Close, window=200)
        df['HMA_200'] = ta.trend.wma_indicator(2*ta.trend.wma_indicator(df.Close, window=round(
            400/2))-ta.trend.wma_indicator(df.Close, window=400), window=round(math.sqrt(400)))
        df['Hull_color'] = np.where(
            df.HMA_200 > df.HMA_200.shift(2), 'green', 'red')

        # boom indicator (from YouTube)

        # make for loop go faster by making lists instead of appending a dataframe
        HP2 = [0]*len(df)
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

        for i in range(2, len(df)):
            number = (1-alpha1222/2)**2*(df.iloc[i].Close-2*df.iloc[i-1].Close+df.iloc[i-2].Close) + 2*(
                1-alpha1222)*HP2[i-1] - (1-alpha1222)**2 * HP2[i-2]
            HP2[i] = number

        HP = HP2
        Filt = [0]*len(df)
        Filt2 = [0]*len(df)
        Peak = [0]*len(df)
        Peak2 = [0]*len(df)

        for i in range(2, len(df)):
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
        df['Q2'] = (X2+K22)/(K22*X2+1)*esize+ey
        X1 = np.where(df_boom.Peak != 0, df_boom.Filt/df_boom.Peak, 0)
        df['Q1'] = (X1+K1)/(K1*X1+1)*esize+ey
        df['Q_trigger'] = ta.trend.sma_indicator(df.Q1, window=2)
        df['cross_above_QT_Q2'] = crossabove(df.Q_trigger, df.Q2)

        # Volitiliy oscilator with relation to the std
        df['Vol_spike'] = df.Close-df.Open
        df['up_stdev'] = df.Vol_spike.rolling(100).std()

    if strat == 'Heiken_stoch':
        OpenH = [df.iloc[0].Open]*len(df)
        CloseH = 1/4*(df.Open+df.High+df.Low+df.Close)
        for i in range(1, len(df)):
            OpenH[i] = (CloseH[i-1]+OpenH[i-1])/2
        df['OpenH'] = OpenH
        df['HighH'] = df[['High', 'OpenH', 'Close']].max(axis=1)
        df['LowH'] = df[['Low', 'OpenH', 'Close']].min(axis=1)
        df['CloseH'] = CloseH

        # ema
        df['EMA_200'] = ta.trend.ema_indicator(df.CloseH, window=200)

        # stoch RSI
        # d is the orange line, k is the blue line in trading view
        df['stoch_k'] = ta.momentum.stochrsi_k(df.CloseH, window=14)
        df['stoch_d'] = ta.momentum.stochrsi_d(df.CloseH, window=14)
        df['rsi_crossover'] = crossabove(df.stoch_k, df.stoch_d)

    # from youtube. Works on 5m candle sticks
    if strat == 'Heiken_ema':
        # heiken ashi candle sticks
        OpenH = [df.iloc[0].Open]*len(df)
        CloseH = 1/4*(df.Open+df.High+df.Low+df.Close)
        for i in range(1, len(df)):
            OpenH[i] = (CloseH[i-1]+OpenH[i-1])/2
        df['OpenH'] = OpenH
        df['HighH'] = df[['High', 'OpenH', 'Close']].max(axis=1)
        df['LowH'] = df[['Low', 'OpenH', 'Close']].min(axis=1)
        df['CloseH'] = CloseH
        df['ColorH'] = np.where(df.OpenH < df.CloseH, 'Green', 'Red')

        # emas
        df['EMA_9'] = ta.trend.ema_indicator(df.CloseH, window=9)
        df['EMA_18'] = ta.trend.ema_indicator(df.CloseH, window=18)
        df['EMA_crossover'] = crossabove(df.EMA_9, df.EMA_18)
        df['EMA_crossbelow'] = crossbelow(df.EMA_9, df.EMA_18)
        df['EMA_9_above'] = np.where(df.EMA_9 > df.EMA_18, 1, 0)

        # trading rule for indicator
        signal = [0]*len(df)
        counter = 0
        for i in range(1, len(df)):
            if (df.iloc[i].EMA_9_above == 1) & (df.iloc[i].LowH > df.iloc[i].EMA_9) & (df.iloc[i].OpenH < df.iloc[i].CloseH):
                counter = counter+1
                signal[i] = counter
            elif df.iloc[i].EMA_9_above == 0:
                counter = 0
        df['signal_count'] = signal
        df['good_signal'] = np.where(df.signal_count == 1, 1, 0)
        good_buy = [0]*len(df)
        js = [1]*len(df)
        ks = [1]*len(df)
        for i in range(1, len(df)):
            j = 1
            k = 1
            if i+2 >= len(df):
                break
            if df.iloc[i].good_signal == 1:
                while ((df.iloc[i+j].ColorH == 'Green') |
                       (df.iloc[i+j].LowH > df.iloc[i+j].EMA_9)):
                    j = j+1
                    if ((df.iloc[i+j].EMA_9_above == 0) |
                        (df.iloc[i+j].CloseH < df.iloc[i+j].EMA_18) |
                            (i+j+1 >= len(df))):
                        j = 0
                        break
                if (j > 0) & (df.iloc[i+j].CloseH > df.iloc[i+j].EMA_18) & (df.iloc[i+j].EMA_9_above == 1):
                    while((df.iloc[i+j+k].ColorH == 'Red') |
                          (df.iloc[i+j+k].CloseH < df.iloc[i+j+k].EMA_9)):
                        k = k+1
                        if (df.iloc[i+j].EMA_9_above == 0) | (df.iloc[i+j].CloseH < df.iloc[i+j].EMA_18):
                            k = 0
                            j = 0
                            break
                    if (j > 0) & (k > 0) & (df.iloc[i+j+k].EMA_9_above == 1):
                        good_buy[i+j+k] = 1

                    js[i] = j
                    ks[i] = k

        df['js'] = js
        df['ks'] = ks
        df['good_buy'] = good_buy

    if strat == 'Magic':
        # macd lines and crossover
        df['fastMA'] = ta.trend.ema_indicator(df.Close, 20)
        df['slowMA'] = ta.trend.ema_indicator(df.Close, 30)
        df['MACD'] = ta.trend.macd(df.Close, window_slow=30, window_fast=20)
        df['MACD_sig'] = ta.trend.sma_indicator(df.MACD, window=10)
        df['MACD_cross'] = crossabove(df.MACD, df.MACD_sig)

        #ADX and DI
        length = 14
        TR = ta.volatility.average_true_range(
            df.High, df.Low, df.Close, window=1)
        DMP = np.where((df.High-df.High.shift(1)) >
                       (df.Low.shift(1)-df.Low), df.High-df.High.shift(1), 0)
        DMP = np.where(DMP < 0, 0, DMP)
        DMM = np.where((df.Low.shift(1)-df.Low) >
                       (df.High-df.High.shift(1)), df.Low.shift(1)-df.Low, 0)
        DMM = np.where(DMM < 0, 0, DMM)
        STR = [0]*len(df)
        SDMP = [0]*len(df)
        SDMM = [0]*len(df)

        for i in range(1, len(df)):
            STR[i] = (STR[i-1]-STR[i-1]/length)+TR[i]
            SDMP[i] = (SDMP[i-1]-SDMP[i-1]/length)+DMP[i]
            SDMM[i] = (SDMM[i-1]-SDMM[i-1]/length)+DMM[i]
        SDMP = pd.Series(SDMP, index=df.index)
        SDMM = pd.Series(SDMM, index=df.index)
        STR = pd.Series(STR, index=df.index)
        DIPlus = SDMP/STR*100
        DIMinus = SDMM/STR*100
        DXtest = pd.Series(abs(DIPlus-DIMinus) /
                           (DIPlus+DIMinus)*100, index=df.index)
        df['ADX'] = ta.trend.sma_indicator(DXtest, length)

        # Bar colors indicator
        length = 200
        MGma = [0]*len(df)

        MGma[0] = df.iloc[0].Close
        for i in range(1, len(df)):
            MGma[i] = MGma[i-1]+(df.iloc[i].Close-MGma[i-1]) / \
                (length*(df.iloc[i].Close/MGma[i-1])**4)
        MGma = pd.Series(MGma, index=df.index)
        TR = pd.Series(ta.volatility.average_true_range(
            df.High, df.Low, df.Close, window=1))
        rangema = ta.trend.ema_indicator(TR, window=200)

        multy = 0.2

        upperk = MGma+rangema*multy
        lowerk = MGma-rangema*multy

        df['BarColor'] = np.where(df.Close > upperk, 'Blue', np.where(
            df.Close < lowerk, 'Red', 'Gray'))


    if strat =='Lazy_Bear': #youtube 80% winrate

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
        i_dict['i1'].append(df.Close[0])
        i_list = list(i_dict.keys())
        #count=0
        for i_key in range(len(i_dict)):
            if i_key == 0:
                for ii in range(1,len(df)):
                    i_dict['i1'].append(c1*df.Close[ii]+c2*i_dict['i1'][ii-1])
            else:
                i_dict[i_list[i_key]].append(df.Close[0])
                for ii in range(1,len(df)):
                    i_dict[i_list[i_key]].append(c1*i_dict[i_list[i_key-1]][ii]+c2*i_dict[i_list[i_key]][ii-1])        
        df['bfr'] = -cd**3*np.array(i_dict['i6'])+c3*np.array(i_dict['i5'])+c4*np.array(i_dict['i4'])+c5*np.array(i_dict['i3'])
        bfrC = []
        bfrC.append('red')
        for jj in range(1,len(df)):
            if df.bfr[jj]>=df.bfr[jj-1]:
                bfrC.append('green')
            else:
                bfrC.append('red')
        df['bfrC'] = bfrC
        
        #pull back strat with the colors and price action
        Close_above = np.where(df.Close>df.bfr,1,0)
        cross_bfr = pd.Series(Close_above).diff()
        df['signal']=np.where(cross_bfr==1,1,0)
        
        #ADX and DI
        length = 14
        TR = ta.volatility.average_true_range(
            df.High, df.Low, df.Close, window=1)
        DMP = np.where((df.High-df.High.shift(1)) >
                       (df.Low.shift(1)-df.Low), df.High-df.High.shift(1), 0)
        DMP = np.where(DMP < 0, 0, DMP)
        DMM = np.where((df.Low.shift(1)-df.Low) >
                       (df.High-df.High.shift(1)), df.Low.shift(1)-df.Low, 0)
        DMM = np.where(DMM < 0, 0, DMM)
        STR = [0]*len(df)
        SDMP = [0]*len(df)
        SDMM = [0]*len(df)

        for i in range(1, len(df)):
            STR[i] = (STR[i-1]-STR[i-1]/length)+TR[i]
            SDMP[i] = (SDMP[i-1]-SDMP[i-1]/length)+DMP[i]
            SDMM[i] = (SDMM[i-1]-SDMM[i-1]/length)+DMM[i]
        SDMP = pd.Series(SDMP, index=df.index)
        SDMM = pd.Series(SDMM, index=df.index)
        STR = pd.Series(STR, index=df.index)
        DIPlus = SDMP/STR*100
        DIMinus = SDMM/STR*100
        DXtest = pd.Series(abs(DIPlus-DIMinus) /
                           (DIPlus+DIMinus)*100, index=df.index)
        df['ADX'] = ta.trend.sma_indicator(DXtest, length)
        df['DIPlus'] = DIPlus
        df['DIMinus'] = DIMinus
        
    if strat =='TraderIQ_1650':
        '''
        Strat Rules:
        #https://www.youtube.com/watch?v=OtQygVyFB9A&list=PLrj3vfjsam-COzIUSdD7MNoys9BjWDt1C&index=1&t=1s&ab_channel=TradeIQ
        #trading indicators: 
            #10 in 1 dif mov avg, 200 ema, 50 wma
            #trader XO macro trend scanner, 
            #stc a better macd
        #trading strat:
            #price above moving average, 
            #50 wma above 200 ema, 
            #pull back into 50 wma not exceed 200 ema, 
            #trader xo makes new buy, 
            #STC must be green, 
            #STC above 80, 
            #STC positive slope 
        #money management after buy signal:
            #SL at recent swing low
            #TP = 1:1 Risk Reward. 
            #When TP is hit, change TP = 2:1 Risk Reward
            #When TP is hit, increase SL to old TP targets
            #ie after one TP is hit, new SL is buy price, when 2 TP is hit, SL is first TP, etc. 
        '''
        #EMA and WMA
        df['EMA_200'] = ta.trend.ema_indicator(df.Close,window = 200)
        df['WMA_50'] = ta.trend.wma_indicator(df.Close, window=50)
        
        # trader XO doesnt show his souce code. What a dick.... Looks like it is just more EMA cross overs tho
        # It looks like the STC is more strict than his anyway and has source code
        
        #STC - dude who wrote the code used shitty variables.... 
        #final output matches exactly what is on the trading view chart tho. 
       # EMA_fast = ta.trend.ema_indicator(df.Close,window = 26)
        #EMA_slow = ta.trend.ema_indicator(df.Close,window = 50)
       # macd = (EMA_fast-EMA_slow)
        
        def aaaa(bbb,fast_len,slow_len):
            fast = ta.trend.ema_indicator(bbb,window = fast_len)
            slow = ta.trend.ema_indicator(bbb,window = slow_len)
            return fast-slow
        lookback_len = 12
        fast_len = 26
        slow_len = 50
        aaa = .5
        
        ccccc = 0
        ddd = 0
        dddddd = 0
        eeeee = 0
        bbbbbb = aaaa(df.Close,fast_len,slow_len)
        ccc = bbbbbb.rolling(lookback_len).min()
        cccc = bbbbbb.rolling(lookback_len).max()-ccc
        ccccc = [0]*len(df)
        ddd = [0]*len(df)
        eeeee = [0]*len(df)
        dddddd = [0]*len(df)
        for i in range(1,len(ccc)):
            if cccc[i]>0:
                ccccc[i] = (bbbbbb[i]-ccc[i])/cccc[i]*100
            else:
                ccccc[i] = ccccc[i-1]
        for j in range(1,len(ddd)):
            ddd[j] = ddd[j-1]+aaa*(ccccc[j]-ddd[j-1])
        ddd = pd.Series(ddd)
        dddd = ddd.rolling(lookback_len).min()
        ddddd = ddd.rolling(lookback_len).max()-dddd
        for k in range(1,len(df)):
            if ddddd[k]>0:
                dddddd[k] = (ddd[k]-dddd[k])/ddddd[k]*100
            else:
                ddddd[k] = ddddd[k-1]
        for m in range(1,len(df)):
            eeeee[m] = eeeee[m-1]+aaa*(dddddd[m]-eeeee[m-1])
        
        df['STC'] = eeeee
        df['color'] = np.where(df.STC>df.STC.shift(),'green','red')
    # Return  the updated dataframe.
    return df


def GetTradesdf(buydates, buyprice, selldates, sellprice):
    tradesdf = pd.DataFrame([buydates, selldates, buyprice, sellprice]).T
    tradesdf.columns = ['buydates', 'selldates', 'buyprices', 'sellprices']
    tradesdf.dropna(inplace=True)
    tradesdf['profit_rel'] = (tradesdf.sellprices -
                              tradesdf.buyprices)/tradesdf.buyprices
    tradesdf['cummulative_profit'] = (tradesdf.profit_rel+1).cumprod()
    tradesdf['profit_net'] = tradesdf.profit_rel - 0.0015
    tradesdf['cummulative_profit_fee'] = (tradesdf.profit_net+1).cumprod()
    tradesdf['profit_bool'] = np.where(tradesdf.profit_rel > 0, True, False)
    tradesdf['profit_bool_fee'] = np.where(
        tradesdf.profit_net > 0, True, False)
    return tradesdf


# define the strategies to get the buy and sell dates and times
def Testing_strat(df, strat):
    '''
    Purpose: Implement trading rules based on indicator values
    - Gets the Buy and Sell dates and prices based on the Youtube strat
    - returnsa DF with all the info to be analyzed on how weel the strat worked
    
    Inputs: df(DataFrame):with indicators, strat(str): must be same as one used in applyindicators()

    Returns: buydates,selldates,buyprice,sellprice for the given strat
    '''
    in_position = False
    buydates = []
    buyprice = []
    selldates = []
    sellprice = []

    # strats go here. Edit for different rules of trading ie adding a stop loss
    # or profit margin. Check if market is trending upwards from the indicators
    # make sure your df has all the indicators needed for the strats.
    # to edit, add the indicators nessasary above, then add strat here.
    if strat == 'High_Low':
        for i in range(len(df)):
            if ~(in_position) & (i+1 < len(df)):
                if ((df.iloc[i].midcross) &
                        (df.iloc[i].Close > df.iloc[i].SMA_50)):
                    buydates.append(df.iloc[i].name)
                    buyprice.append(df.iloc[i].Close)
                    TP = df.iloc[i].Close*1.02
                    SL = df.iloc[i].Close*.99
                    in_position = True
                    continue

            if (in_position) & (i+1 < len(df)):
                if (df.iloc[i].Low < SL):
                    sellprice.append(SL)
                    selldates.append(df.iloc[i].name)
                    in_position = False
                elif (df.iloc[i].High > TP):
                    sellprice.append(TP)
                    selldates.append(df.iloc[i].name)
                    in_position = False

    if strat == 'Boom':
        for i in range(2, len(df)):
            if ~(in_position) & (i+1 < len(df)):
                if ((df.iloc[i].Q_trigger >= df.iloc[i].Q2) &
                    (df.iloc[i].cross_above_QT_Q2 == 1) &
                    (df.iloc[i].Close > df.iloc[i].HMA_200) &
                    (df.iloc[i].Hull_color == 'green') &
                    (max(df[i-1:i].Vol_spike) > df.iloc[i].up_stdev)):
                    buydates.append(df.iloc[i].name)
                    buyprice.append(df.iloc[i].Close)
                    SL = min(df[i-30:i].Low)*.998
                    Risk = 1-(SL/df.iloc[i].Close)
                    TP = df.iloc[i].Close+df.iloc[i].Close*Risk*2
                    #TSL = SL

                    in_position = True
                    continue

            if (in_position) & (i+1 < len(df)):
                if (df.iloc[i].Low < SL):
                    sellprice.append(SL)
                    selldates.append(df.iloc[i].name)
                    in_position = False
                elif (df.iloc[i].High > TP):
                    sellprice.append(TP)
                    selldates.append(df.iloc[i].name)
                    in_position = False

    if strat == 'Heiken_stoch':
        for i in range(2, len(df)):
            if ~(in_position) & (i+1 < len(df)):
                if ((df.iloc[i].rsi_crossover == 1) &
                    ((df.iloc[i].stoch_k <= .2) |
                     (df.iloc[i].stoch_d <= .2)) &
                    (df.iloc[i].CloseH-df.iloc[i].OpenH > df.iloc[i-1].CloseH-df.iloc[i-1].OpenH) &
                    (df.iloc[i].CloseH > df.iloc[i].OpenH) &
                    (df.iloc[i-1].CloseH > df.iloc[i-1].OpenH) &
                        (df.iloc[i].CloseH >= df.iloc[i].EMA_200)):

                    buydates.append(df.iloc[i].name)
                    buyprice.append(df.iloc[i].Close)
                    SL = min(min(df[i-5:i].Low), df.iloc[i].Close*.995)
                    Risk = 1-(SL/df.iloc[i].Close)
                    TP = df.iloc[i].Close+df.iloc[i].Close*Risk*1.5

                    in_position = True
                    continue

            if (in_position) & (i+1 < len(df)):
                if (df.iloc[i].Low < SL):
                    sellprice.append(SL)
                    selldates.append(df.iloc[i].name)
                    in_position = False
                elif (df.iloc[i].High > TP):
                    sellprice.append(TP)
                    selldates.append(df.iloc[i].name)
                    in_position = False

    if strat == 'Heiken_ema':
        for i in range(1, len(df)):
            if ~(in_position) & (i+1 < len(df)):
                if (df.iloc[i].good_buy == 1):

                    buydates.append(df.iloc[i].name)
                    buyprice.append(df.iloc[i].Close)
                    SL = min(df.iloc[i-1].Low, df.iloc[i].Close*.998)
                    Risk = 1-(SL/df.iloc[i].Close)
                    TP = df.iloc[i].Close+df.iloc[i].Close*Risk*2

                    in_position = True
                    continue

            if (in_position) & (i+1 < len(df)):
                if (df.iloc[i].Low < SL):
                    sellprice.append(SL)
                    selldates.append(df.iloc[i].name)
                    in_position = False
                elif (df.iloc[i].High > TP):
                    sellprice.append(TP)
                    selldates.append(df.iloc[i].name)
                    in_position = False

    if strat == 'Magic':
        for i in range(200, len(df)):
            if ~(in_position) & (i+1 < len(df)):
                if (((df.iloc[i].BarColor == 'Blue') | (df.iloc[i].BarColor == 'Gray')) &
                    (df.iloc[i].ADX >= 20) &
                    (df.iloc[i].MACD_cross == 1) &
                        ((df.iloc[i].MACD > 0) | (df.iloc[i].MACD_sig > 0))):

                    buydates.append(df.iloc[i].name)
                    buyprice.append(df.iloc[i].Close)
                    SL = min(min(df[i-10:i].Low), df.iloc[i].Close*.9975)
                    Risk = 1-(SL/df.iloc[i].Close)
                    TP = df.iloc[i].Close+df.iloc[i].Close*Risk*2

                    in_position = True
                    continue

            if (in_position) & (i+1 < len(df)):
                if (df.iloc[i].Low < SL):
                    sellprice.append(SL)
                    selldates.append(df.iloc[i].name)
                    in_position = False
                elif (df.iloc[i].High > TP):
                    sellprice.append(TP)
                    selldates.append(df.iloc[i].name)
                    in_position = False
                    
    if strat == 'Lazy_Bear':
        for i in range(4, len(df)):
            if ~(in_position) & (i+1 < len(df)):
                if ((df.iloc[i].bfrC=='green')&
                    (df.iloc[i].signal ==1)&
                    (df.iloc[i].DIPlus>df.iloc[i].DIMinus)&
                    (df.iloc[i].ADX>15)):

                    buydates.append(df.iloc[i].name)
                    buyprice.append(df.iloc[i].Close)
                    SL = min(min(df[i-5:i].Low)*.999, df.iloc[i].Close*.995)
                    Risk = 1-(SL/df.iloc[i].Close)
                    TP = df.iloc[i].Close+df.iloc[i].Close*Risk*2
                    in_position = True
                    continue

            if (in_position) & (i+1 < len(df)):
                if (df.iloc[i].Low < SL):
                    sellprice.append(SL)
                    selldates.append(df.iloc[i].name)
                    in_position = False
                elif (df.iloc[i].High > TP):
                    sellprice.append(TP)
                    selldates.append(df.iloc[i].name)
                    in_position = False                        

    tradesdf = GetTradesdf(buydates, buyprice, selldates, sellprice)
    return tradesdf


def Plot_visual(df, tradesdf, symbol='Coin Title'):

    plt.style.use('dark_background')
    plt.figure(figsize=(20, 10))
    plt.title(symbol)
    plt.plot(df[['SMA_50']])
    plt.scatter(tradesdf.buydates, tradesdf.buyprices,
                marker='^', color='g', s=200)
    plt.scatter(tradesdf.selldates, tradesdf.sellprices,
                marker='v', color='r', s=200)
    plt.grid()
    plt.show()


def Buy_and_Hold(df):
    buy = df.Close[1]
    sell = df.Close[-1]
    profit = ((sell-buy)/buy-0.0015)+1
    return profit


def trades_stats(tradesdf):
    statsdict = {}
    statsdict['profit_no_fee'] = (tradesdf.profit_rel+1).prod()
    statsdict['profit_fee'] = (tradesdf.profit_net+1).prod()
    statsdict['winrate'] = tradesdf.profit_bool.sum()/len(tradesdf)
    statsdict['buyhold'] = Buy_and_Hold(df)
    return statsdict

# %%
# testing with data single symbol


df = getdata(symbol='BTCUSDT', interval='5m', lookback='200')
strat = 'TraderIQ_1650'
df = applyindicators(df, strat=strat)
tradesdf = Testing_strat(df, strat=strat)
#Plot_visual(df, tradesdf)
stats = trades_stats(tradesdf)


# %% Mega Backtest
#tests for however many symbol pairs you want
#could be editted in the future to check hyperparametersand find optimal
symbols = ['BNBUSDT', 'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'DOGEUSDT']
strat = 'Lazy_Bear'
Dict_for_strat = {}
for symbol in symbols:
    Dict_for_strat[symbol] = {}
    df = getdata(symbol, interval='1h', lookback='1000')
    df = applyindicators(df, strat=strat)

    Dict_for_strat[symbol]['tradesdf'] = Testing_strat(df, strat=strat)
    Dict_for_strat[symbol]['stats'] = trades_stats(Dict_for_strat[symbol]['tradesdf'])


# %% Plot all of them
Plot_visual(df, tradesdf)
