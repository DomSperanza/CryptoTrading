# -*- coding: utf-8 -*-
"""
Created on Fri Jun 24 18:28:11 2022

@author: dvspe
Purpose:
    Make an easily editable backtesting script that will allow me to see the effectiveness
    of trading strategies before implementing them. All functions and variables 
    can live in this script and binance functions can be ported over
    
    Going to be using methods similar to Algovibes from youtube to backtest
    
Packages needed: ta, python-binance, pandas, numpy, etc
"""

#%% Import Packages needed
import ta
import pandas as pd
import numpy as np
import os
from binance.client import Client
from scipy.stats import zscore
import matplotlib.pyplot as plt
from finta import TA as ta2

#set up the correct dirrectory
os.chdir(r'C:\Users\dvspe\Desktop\Python_Trading')

#%% Set up the Client from binance to get the data. No key needed
client = Client()
#client2 = Client()
#check the results with the paper trading account as well
#client2.API_URL = 'https://testnet.binance.vision/api'


#%% Keep all functions here  with labels as to what they do.
def getdata(symbol,interval = '1m', lookback = '400',client = client):
    frame = pd.DataFrame(client.get_historical_klines(symbol,
                                                      interval,
                                                      lookback +' hours ago UTC'))
    frame = frame.iloc[:,0:6]
    frame.columns = ['Time','Open','High','Low','Close','Volume']
    frame.set_index('Time',inplace = True)
    frame.index = pd.to_datetime(frame.index,unit = 'ms')
    frame = frame.astype(float)
    #cleans up the data frame from stupid values
    #z_scores = zscore(frame)
    #abs_z_scores = np.abs(z_scores)
    #filtered_entries = (abs_z_scores < 3).all(axis=1)
    #frame = frame[filtered_entries]
    return frame  

#Checks to see if there is a crossover of the signal line
def crossabove(fast,slow):
    series = pd.Series(np.where(fast>slow,1,0))
    series = series.diff()
    series = np.where(series==1,1,0) 
    return series

def crossbelow(fast,slow):
    series = pd.Series(np.where(fast<slow,1,0))
    series = series.diff()
    series = np.where(series==1,1,0)
    return series


def applyindicators(df):
    lookback = 5
    heikin = True
    if heikin:
        df2 = df.copy()
        df['CloseH'] = 1/4*(df.Open+df.High+df.Low+df.Close)
        df['OpenH'] = 1/2*(df.Open.shift()+df.Close.shift())
        df['HighH'] = df[['High','Open','Close']].max(axis = 1)
        df['LowH'] = df[['Low','Open','Close']].min(axis = 1)
        df2.Close = df['CloseH']
        df2.Open = df['OpenH']
        df2.High= df['HighH']
        df2.Low = df['LowH']
        
    
    
    #SMA indicators
    df['SMA_150'] = df.Close.rolling(150).mean()
    df['SMA_150_slope'] = df.SMA_150.diff(lookback)/df.SMA_150
    df['SMA_25'] = df.Close.rolling(25).mean()
    df['SMA_25_slope'] = df.SMA_25.diff(lookback)/df.SMA_25
    df['SMA_50']=df.Close.rolling(50).mean()
    df['SMA_50_slope'] = df.SMA_50.diff(lookback)/df.SMA_50
    df['SMA_100']=df.Close.rolling(100).mean()
    df['SMA_100_slope'] = df.SMA_100.diff(lookback)/df.SMA_100
    df['SMA_20'] = df.Close.rolling(20).mean()
    df['SMA_30'] = df.Close.rolling(30).mean()
    df['SMA_5'] = df.Close.rolling(5).mean()
    df['SMA_8'] = df.Close.rolling(8).mean()
    df['SMA_13'] = df.Close.rolling(13).mean()
    df['SMA_13_slope'] =df.SMA_13.diff(13)/13
    df['SMA_5_slope'] = df.SMA_5.diff(5)/5
    df['SMA_50'] = ta.trend.sma_indicator(df.Close,window = 50)
    df['SMA_50_slope'] = df.SMA_50.diff(lookback)/df.SMA_50
    
    #EMA indicators
    df['EMA_25'] = ta.trend.ema_indicator(df.Close,window = 25)
    df['EMA_25_slope'] = (df.EMA_25.diff(lookback)/lookback)/df.Close*100
    df['EMA_50'] = ta.trend.ema_indicator(df.Close,window = 50)
    df['EMA_50_slope'] = df.EMA_50.diff(lookback)/lookback/df.Close*100
    df['EMA_100'] = ta.trend.ema_indicator(df.Close,window = 100)
    df['EMA_100_slope'] = df.EMA_100.diff(lookback)/lookback/df.Close*100
    df['EMA_2'] = ta.trend.ema_indicator(df.Close,window = 2)
    #df['EMA_50_above']
    
    #Bollinger Bands
    df['stddev_20'] = df.Close.rolling(20).std()
    df['Upper_20_std'] = df.SMA_20+2*df.stddev_20
    df['Lower_20_std'] = df.SMA_20-2*df.stddev_20
    df['stddev_30'] = df.Close.rolling(20).std()
    df['Upper_30_std'] = df.SMA_30+2*df.stddev_30
    df['Lower_30_std'] = df.SMA_30-2*df.stddev_30
    
    #Rsi indicators
    df['rsi_2']= ta.momentum.rsi(df.Close,2)
    df['rsi_9'] = ta.momentum.rsi(df.Close,9)
    df['rsi_10']= ta.momentum.rsi(df.Close,10)
    df['rsi_11']= ta.momentum.rsi(df.Close,11)
    df['rsi_13'] = ta.momentum.rsi(df.Close,13)
    df['rsi_100'] = ta.momentum.rsi(df.Close,100)
    df['rsi_25'] = ta.momentum.rsi(df.Close,25)
    
    
    # MACD indicators and cross overs. 
    df['macd'] = ta.trend.macd_diff(df.Close,27,50)
    df['macd_signal'] = ta.trend.macd_signal(df.Close,27,50)
    df['macd_above_signal'] = np.where(df.macd>df.macd_signal,1,0)
    df['macd_cross_below'] = np.where(df.macd_above_signal.diff()==-1,1,0)
    df['macd_cross_above'] = np.where(df.macd_above_signal.diff()==1,1,0)
    
    # Stochasic rsi indicators
    df['rsi_d_14'] = ta.momentum.stochrsi_d(df.Close,window = 14)
    df['rsi_k_14'] = ta.momentum.stochrsi_k(df.Close,window = 14)
    df['kd_crossover'] = crossabove(df.rsi_d_14,df.rsi_k_14)

    #rolling high low mid
    df['rollhigh'] = df.High.rolling(15).max()
    df['rolllow'] = df.Low.rolling(15).min()
    df['mid'] = (df.rollhigh+df.rolllow)/2
    df['highapproach'] = np.where(df.Close>df.rollhigh*0.999,1,0)
    df['close_a_mid'] = np.where(df.Close>df.mid,1,0)
    df['midcross'] = df.close_a_mid.diff()==1
    
    #Chandelier Exit
    #df['ATR_1'] = ta.volatility.average_true_range(df.High, df.Low, df.Close,window = 1)
    #df['ATR_mult'] = 1.85
    #df['max_1dayLow'] = df.Low.shift(1).rolling(2).max()
    #df['Chandelier_short_exit'] = df.max_1dayLow + (df.ATR_1*df.ATR_mult)
    chan_info = ta2.CHANDELIER(df2,short_period = 10,long_period = 10,k = 2)
    df = pd.concat([df,chan_info],axis = 1,ignore_index = False)
    df.rename(columns = {'Short.':'Chan_Short','Long.':'Chan_Long'},inplace = True)
    
    
    #Atr trailing stop strat indicators
    df['atr'] = ta.volatility.average_true_range(df.High, df.Low, df.Close,window = 10)
    df['nLoss'] = 2*df.atr
    df['atr_trailing'] = 0
    for i in range(1,len(df)):
        if (df.Close[i]>df.atr_trailing[i-1]) and (df.Close[i-1]>df.atr_trailing[i-1]):
            df.atr_trailing.iloc[i] = max(df.atr_trailing[i-1],df.Close[i]-df.nLoss[i])
        elif (df.Close[i]<df.atr_trailing[i-1]) and df.Close[i-1]<df.atr_trailing[i-1]:
            df.atr_trailing.iloc[i] = min(df.atr_trailing[i-1],df.Close[i]+df.nLoss[i])
        elif (df.Close[i]>df.atr_trailing[i-1]):
            df.atr_trailing.iloc[i] = df.Close[i]-df.nLoss[i]
        else:
            df.atr_trailing.iloc[i] = df.Close[i]+df.nLoss[i]
    df['ema_atr_cross_above'] = crossabove(df.EMA_2, df.atr_trailing)
    df['ema_atr_cross_below'] = crossbelow(df.EMA_2, df.atr_trailing)
    return df

def strat(df,strat):
    in_position = False
    buydates = []
    selldates = []
    
    #strats go here. Edit for different rules of trading ie adding a stop loss
    #or profit margin. Check if market is trending upwards from the indicators
    #make sure your df has all the indicators needed for the strats.
    #to edit, add the indicators nessasary above, then add strat here. 
    if strat == 'High_Low':
        for i in range(len(df)):
            if ~(in_position) & (i+1<len(df)):
                if ((df.iloc[i].midcross) &
                    (df.iloc[i].Close>df.iloc[i].SMA_50)&
                    (df.iloc[i].SMA_50_slope>.001)):
                    buydates.append(df.iloc[i+1].name)
                    TP = df.iloc[i].Close*1.02
                    SL = df.iloc[i].Close*.99
                    in_position = True
                
            if (in_position) & (i+1<len(df)):
                if ((df.iloc[i].highapproach) | \
                    (df.iloc[i].Close<=SL)) | \
                    (df.iloc[i].Close>=TP):
                        
                    selldates.append(df.iloc[i+1].name)
                    in_position = False
    
    if strat == 'Bollinger_Bands':
        for i in range(len(df)):
            if ~(in_position)&(i+1<len(df)):
                if ((df.iloc[i].Close>df.iloc[i].SMA_50)&
                    (df.iloc[i].Close<df.iloc[i].Lower_20_std) &
                    (df.iloc[i].Close>=df.iloc[i-1].Low)&
                    (df.iloc[i].SMA_50_slope>.001)):
                    buydates.append(df.iloc[i+1].name)
                    TP = df.iloc[i+1].Upper_20_std*1.01
                    TSL = df.iloc[i+1].Close*.985
                    in_position = True 
                    continue
                
            if (in_position)&(i+1<len(df)):
                TP = df.iloc[i+1].Upper_20_std*1.01
                testTSL = df.iloc[i].Close*.985
                if (testTSL>TSL):
                    TSL = testTSL
                if((df.iloc[i].Close<=TSL)|
                   (df.iloc[i].Close>=TP)):
                    selldates.append(df.iloc[i+1].name)
                    in_position = False
    
    if strat == 'Bollinger_Bands_RSI':
        for i in range(len(df)):
            if ~(in_position)&(i+1<len(df)):
                if ((df.iloc[i].Close>df.iloc[i].SMA_100)&
                    (df.iloc[i].Close<df.iloc[i].Lower_20_std*1.01) &
                    (df.iloc[i].rsi_13<30)&
                    (df.iloc[i].SMA_100_slope>.0001)):
                    buydates.append(df.iloc[i+1].name)
                    TP = df.iloc[i+1].Close*1.03
                    TSL = df.iloc[i+1].Close*.985
                    in_position = True 
                    continue
                
            if (in_position)&(i+1<len(df)):
                testTSL = df.iloc[i].Close*.985
                if (testTSL>TSL):
                    TSL = testTSL
                if((df.iloc[i].Close<=TSL)|
                   (df.iloc[i].Close>=TP)):
                    selldates.append(df.iloc[i+1].name)
                    in_position = False
                    
                    
    if strat == 'MACD':
        for i in range(len(df)):
            if ~(in_position)&(i+1<len(df)):
                if ((df.iloc[i].macd_above_signal==1)&
                    (df.iloc[i].macd<0)&
                    (df.iloc[i].macd_signal<0)&
                    (df.iloc[i].Close>df.iloc[i].EMA_100)&
                    (df.iloc[i].EMA_100_slope>0)):
                    buydates.append(df.iloc[i+1].name)
                    TP = df.iloc[i+1].Close*1.0125
                    TSL = df.iloc[i+1].Close*.99
                    in_position = True 
                    continue
                
            if (in_position)&(i+1<len(df)):
                testTSL = df.iloc[i].Close*.99
                if (testTSL>TSL):
                    TSL = testTSL
                if((df.iloc[i].Close<=TSL)|
                   (df.iloc[i].Close>=TP)):
                    selldates.append(df.iloc[i+1].name)
                    in_position = False
                    
                    
    if strat == 'EMA_MACD':
        for i in range(len(df)):
            if ~(in_position)&(i+1<len(df)):
                if ((df.iloc[i].macd_cross_above==1)&
                    (df.iloc[i].Close>df.iloc[i].EMA_100)&
                    (df.iloc[i].EMA_100_slope>0)):
                    buydates.append(df.iloc[i+1].name)
                    TP = df.iloc[i+1].Close*1.02
                    TSL = df.iloc[i+1].Close*.98
                    in_position = True 
                    continue
                
            if (in_position)&(i+1<len(df)):
                testTSL = df.iloc[i].Close*.99
                if (testTSL>TSL):
                    TSL = testTSL
                if((df.iloc[i].Close<=TSL)|
                   (df.iloc[i].Close>=TP)):
                    selldates.append(df.iloc[i+1].name)
                    in_position = False
                    
                    
    if strat == 'Chan_Rsi':
        for i in range(len(df)):
            if ~(in_position)&(i+1<len(df)):
                if ((df.iloc[i].Chan_Short<df.iloc[i].CloseH)&
                    #(df.iloc[i].rsi_25>df.iloc[i].rsi_100)&
                    #(df.iloc[i].rsi_25<50)&
                    #(df.iloc[i].rsi_100<50)&
                    (df.iloc[i].EMA_100<df.iloc[i].CloseH)):
                    buydates.append(df.iloc[i+1].name)
                    TP = df.iloc[i+1].Open*1.0125
                    TSL = df.iloc[i+1].Open*.99
                    in_position = True 
                    continue
                
            if (in_position)&(i+1<len(df)):
                testTSL = df.iloc[i].Close*.99
                if (testTSL>TSL):
                    TSL = testTSL
                if((df.iloc[i].Close<=TSL)|
                   ((df.iloc[i].Chan_Long>df.iloc[i].CloseH)&
                   (df.iloc[i].Close>=TP))):
                    selldates.append(df.iloc[i+1].name)
                    in_position = False  
                    
                    
    if strat == 'UT_Bot':
        for i in range(len(df)):
            if ~(in_position)&(i+1<len(df)):
                #buying conditions
                if ((df.iloc[i].Close>df.iloc[i].atr_trailing)&
                    (df.iloc[i].ema_atr_cross_below==1)&
                    #(df.iloc[i].macd>0)&
                    (df.iloc[i].Close>df.iloc[i].EMA_100)):
                    buydates.append(df.iloc[i+1].name)
                    TP = df.iloc[i+1].Open*1.02
                    TSL = df.iloc[i+1].Open*.99
                    in_position = True 
                    continue
                
            if (in_position)&(i+1<len(df)):
                testTSL = df.iloc[i].Close*.99
                if (testTSL>TSL):
                    TSL = testTSL
                if((df.iloc[i].Close<=TSL)|
                   ((df.iloc[i].Close<df.iloc[i].atr_trailing) &
                    (df.iloc[i].ema_atr_cross_below == 1))):
                    selldates.append(df.iloc[i+1].name)
                    in_position = False  
                    
    return buydates,selldates


def Plot_visual(df,buydates,selldates,symbol = 'Coin Title'):
    
    plt.style.use('dark_background')
    plt.figure(figsize=(20,10))
    plt.title(symbol)
    plt.plot(df[['Close','EMA_100']])
    plt.scatter(buydates, df.loc[buydates].Open, marker = '^',color = 'g', s = 200)
    plt.scatter(selldates, df.loc[selldates].Open, marker = 'v',color = 'r', s = 200)
    plt.grid()
    plt.show()
    
    
def GetTradesdf(df,buydates,selldates):
    tradesdf = pd.DataFrame([buydates,selldates,df.loc[buydates].Open,df.loc[selldates].Open]).T
    tradesdf.columns = ['buydates','selldates','buyprices','sellprices' ]
    tradesdf.dropna(inplace = True)
    tradesdf['profit_rel'] = (tradesdf.sellprices - tradesdf.buyprices)/tradesdf.buyprices
    tradesdf['profit_net'] = tradesdf.profit_rel -0.0015 
    tradesdf['cummulative_profit'] = (tradesdf.profit_net+1).cumprod()
    tradesdf['profit_bool'] = np.where(tradesdf.profit_net>0,True,False)
    return tradesdf


def Buy_and_Hold(df):
    buy = df.Close[1]
    sell = df.Close[-1]
    profit = ((sell-buy)/buy-0.0015)+1
    return profit



#%% Set up the Dataframes with the indicators

#symbol = 'BTCUSDT'
strategy = 'UT_Bot'
symbols = ['BNBUSDT','BTCUSDT','ETHUSDT','SOLUSDT']
Dict_for_strat = {}
for symbol in symbols:
    Dict_for_strat[symbol] = {}
    df = getdata(symbol,interval = '5m',lookback = '100')
    df = applyindicators(df)
    


#%% Make the buying and selling dataframes
    Dict_for_strat[symbol]['buydates'],Dict_for_strat[symbol]['selldates'] = strat(df,'UT_Bot')

#%% Plot the backtesting technique
    Plot_visual(df, Dict_for_strat[symbol]['buydates'], Dict_for_strat[symbol]['selldates'], symbol = symbol)

#%% Get the trades dataframe to find out the profit of everything. 
    Dict_for_strat[symbol]['tradesdf'] = GetTradesdf(df, Dict_for_strat[symbol]['buydates'], Dict_for_strat[symbol]['selldates'])
    Dict_for_strat[symbol]['profit'] = (Dict_for_strat[symbol]['tradesdf'].profit_net+1).prod()
    Dict_for_strat[symbol]['winrate'] = Dict_for_strat[symbol]['tradesdf'].profit_bool.sum()/len(Dict_for_strat[symbol]['tradesdf'])
    Dict_for_strat[symbol]['buyhold'] = Buy_and_Hold(df)

