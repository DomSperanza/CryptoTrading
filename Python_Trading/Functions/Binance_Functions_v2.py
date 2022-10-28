# -*- coding: utf-8 -*-
"""
Created on Sun Jun 19 14:50:30 2022

@author: dvspe
Purpose:
    Keep all of the Binance functions accessable for creating scripts
    Tidy up the functions that i have already written and add in other indicators
    
    
Packages:
    binance-client, pandas, os
"""

import pandas as pd
from binance import Client
import ta
import numpy as np
from scipy.stats import zscore
import sqlalchemy
from binance import ThreadedWebsocketManager
import time
import matplotlib.pyplot as plt
from datetime import datetime,timezone
from finta import TA as ta2
import math


#changing position
def changepos(symbol,order,tradesdf):
    if order['side']=='BUY':
        tradesdf.loc[tradesdf['symbol']==symbol,'open_trade']=True
        tradesdf.loc[tradesdf['symbol']==symbol,'quantity']=float(order['origQty'])
    else:
        tradesdf.loc[tradesdf['symbol']==symbol,'open_trade']=False
        tradesdf.loc[tradesdf['symbol']==symbol,'quantity']=0
    return tradesdf
        
        
def getminutedata(symbol,interval, lookback,client):
    frame = pd.DataFrame(client.get_historical_klines(symbol,
                                                      interval,
                                                      lookback +' min ago UTC'))
    

    frame = frame.iloc[:,0:6]
    frame.columns = ['Time','Open','High','Low','Close','Volume']
    frame.set_index('Time',inplace = True)
    frame.index = pd.to_datetime(frame.index,unit = 'ms')
    frame = frame.astype(float)
    #This was to filter out outliers in the data. Mainly used for the fake account cause
    #some of the values were BS
    
    #z_scores = zscore(frame)
    # abs_z_scores = np.abs(z_scores)
    # filtered_entries = (abs_z_scores < 4).all(axis=1)
    # frame = frame[filtered_entries]
    
    return frame      


def crossabove(fast, slow):
    series = pd.Series(np.where(fast > slow, 1, 0))
    series = series.diff()
    series = np.where(series == 1, 1, 0)
    return series


def crossbelow(fast, slow):
    series = pd.Series(np.where(fast < slow, 1, 0))
    series = series.diff()
    series = np.where(series == 1, 1, 0)
    return series


def applyindicators(df, strat):
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

    #youtube 80% winrate. 1 hr candlesticks. only on ETHUSDT
    if strat =='Lazy_Bear': 
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
        
    # Return  the updated dataframe.
    return df
    
    
    
#need to update based on what i have in backtesting
def conditions(df_indicators, strat = 'basic'):
    
    if strat == 'High_Low':
       df_indicators['Buy'] = np.where(((df_indicators.midcross==1)&
                                        (df_indicators.Close>df_indicators.SMA_50)),1,0) 
    
    if strat == 'basic':
        df_indicators['Buy'] = np.where(((df_indicators.Close<df_indicators.Lower_20_std*1)&
                          (df_indicators.Close*1>df_indicators.SMA_MAX))&
                          ((df_indicators.rsi_2<10) & (df_indicators.rsi_10<20)),1,0) 
    
        df_indicators['Sell'] = np.where((df_indicators.rsi_10>80),1,0)
        
    elif strat == 'StochRSI+ShortSMA':
        df_indicators['Buy'] = np.where(((df_indicators.Close>df_indicators.SMA_MAX) &
                                        (df_indicators.Close<df_indicators.SMA_13) &
                                        (df_indicators.SMA_5_slope>0) &
                                        (df_indicators.rsi_9<40)),1,0)
        
        df_indicators['Sell'] = np.where(((df_indicators.SMA_13_slope<0) &
                                        (df_indicators.rsi_9>70)),1,0)
        
    elif strat == 'macd+shortSMA+rsi':
        df_indicators['Buy'] = np.where(((df_indicators.Close>df_indicators.SMA_MAX) &
                                        (df_indicators.Close<df_indicators.SMA_13) &
                                        (df_indicators.SMA_5_slope>0) &
                                        (df_indicators.macd<0.5)&
                                        (df_indicators.rsi_9<40)),1,0)
        
        df_indicators['Sell'] = np.where(((df_indicators.SMA_13_slope<0) &
                                          (df_indicators.rsi_9>70)&
                                          (df_indicators.macd>0.7)),1,0)
        
    elif strat == 'short_long_EMA':
        df_indicators['Buy'] = np.where(((df_indicators.Close<df_indicators.EMA_25) &
                                         (df_indicators.Close>df_indicators.EMA_50) &
                                         (df_indicators.Close>df_indicators.EMA_100) &
                                         (df_indicators.EMA_25>df_indicators.EMA_50) &
                                         (df_indicators.EMA_50>df_indicators.EMA_100) &
                                         (df_indicators.EMA_25_slope>.01) &
                                         (df_indicators.EMA_50_slope>.0075) &
                                         (df_indicators.EMA_100>0.005)),1,0)
        
        df_indicators['Sell'] = np.where(df_indicators.Close<df_indicators.EMA_100*1.004,1,0)
    
    elif strat == 'macd':
        df_indicators['Buy'] = np.where(((df_indicators.macd_above_signal==1)&
                                         (df_indicators.macd<0)&
                                         (df_indicators.macd_signal<0)&
                                         (df_indicators.Close>df_indicators.EMA_100)&
                                         (df_indicators.EMA_100_slope>0)),1,0)
        #never have a sell signal. Just use the stoploss and target profit. 
        df_indicators['Sell'] = np.where(df_indicators.Close>0,0,1)
              
    elif strat == 'chan':
        df_indicators['Buy'] = np.where(((df_indicators.Chan_Short<df_indicators.Close)&
                                         #(df_indicators.rsi_25>df_indicators.rsi_100)&
                                         (df_indicators.EMA_100<df_indicators.Close)),1,0)
        df_indicators['Sell'] = np.where(df_indicators.Close<df_indicators.Chan_Long,1,0)
        
        
    
    return(df_indicators)


#%%
#pull client data for trailing stop loss. 
#Use this to do a trailing stoploss
#Right now it is set up at a 1% trailing stop loss always. 
#
def tsl(symbol,client,df = pd.DataFrame(),percent = .99):
    if len(df)==0:
        df = pd.DataFrame(client.get_ticker(symbol = symbol),index = [0])
        df = df[['closeTime','lastPrice']]
        df.closeTime = pd.to_datetime(df.closeTime,unit = 'ms')
        df['lastPrice'] = float(df['lastPrice'])
        df['Benchmark'] = df['lastPrice'].cummax()
        df['TSL'] = df['Benchmark']*percent
    else:
        df2 = pd.DataFrame(client.get_ticker(symbol = symbol),index = [0])
        df2 = df2[['closeTime','lastPrice']]
        df2.closeTime = pd.to_datetime(df2.closeTime,unit = 'ms')
        df2['lastPrice'] = float(df2['lastPrice'])
        df = pd.concat([df,df2])
        df['Benchmark'] = df['lastPrice'].cummax()
        df['TSL'] = df['Benchmark']*percent
    return df
        
        
#%% MAKES SURE ORDER IS NOT GOING TO PRODUCE AN ERROR   

#Function to get the limit order price that is properly rounded. 
def pricecalc(symbol,client, limit = .99975):
    raw_price = float(client.get_symbol_ticker(symbol = symbol)['price'])
    dec_len = len(str(raw_price).split('.')[1])
    price = raw_price*limit
    return round(price,dec_len)

def right_rounding(Lotsize):
    split = str(Lotsize).split('.')
    if float(split[0])==1:
        return 0
    else:
        return len(split[1])
    
def quantitycalc(symbol, investment,client):
    info = client.get_symbol_info(symbol = symbol)
    Lotsize = float([i for i in info['filters'] if i['filterType']=='LOT_SIZE'][0]['minQty'])
    Lotsize = np.format_float_positional(Lotsize)
    price = pricecalc(symbol,client)
    qty = round(investment/price,right_rounding(Lotsize))
    return qty


#%% MAKES AN ORDER
#making a by limit order
def buy(symbol,investment,client,tradesdf):
    order = client.order_limit_buy(
        symbol = symbol,
        price = pricecalc(symbol,client),
        quantity = quantitycalc(symbol,investment,client))
    changepos(symbol, order, tradesdf)
    print(order)
    return(order)

#making a market sell
def sell(symbol,client,tradesdf):
    order = client.create_order(
        symbol = symbol,
        side = "SELL",
        type = 'MARKET',
        quantity = tradesdf[tradesdf['symbol']==symbol]['quantity'].values[0])
    changepos(symbol,order,tradesdf)
    print(order)
    return(order)



#%% BUILD A TRADER FUNCTION TO IMPLEMENT THE STRATEGY.
#This portion needs to be updated. 

def trader(investment,client,tradesdf,tsl_dicts,strategy = 'basic',order = None):
    #INITIALIZE THE DICTIONARY AND MAKE A DATAFRAME IN EACH PART OF THE DICT
    indicators_dict ={}
    for symbol in tradesdf.symbol:
        indicators_dict[symbol] = pd.DataFrame()
        
        
    #IF YOU ARE IN A POSITION, CHECK TO SEE IF YOU SHOULD EXIT THE POSITION
    #baseline money management should be SL at recent swing low or hitting the take profit target based on risk
    
    for symbol in tradesdf[tradesdf.open_trade == True].symbol:        
        indicators_dict[symbol] = getminutedata(symbol, '5m', '2000', client)
        indicators_dict[symbol]  = applyindicators(indicators_dict[symbol])
        indicators_dict[symbol]  = conditions(indicators_dict[symbol] ,strategy)
        tsl_dicts[symbol] = tsl(symbol, client,df = tsl_dicts[symbol])
        lastrow = indicators_dict[symbol].tail(1)
        TSL_Sell = True in (tsl_dicts[symbol]['lastPrice']<tsl_dicts[symbol]['TSL']).values 
        # get the purchase order price and look to make a 2.5% profit on the trade if it gets that high
        target_profit = float(client.get_my_trades(symbol = symbol)[-1]['price'])*1.015
        stop_loss = float(client.get_my_trades(symbol = symbol)[-1]['price'])*.99

        if (((lastrow['Sell'].values[0]==1) & (lastrow['Close'].values[0]>target_profit))| (TSL_Sell == True))\
                and not client.get_open_orders(symbol = symbol):
            sell_order = sell(symbol,client,tradesdf)
            tsl_dicts[symbol] = pd.DataFrame()
        else:
            sell_order = order
    
    #IF NOT A POSITION, CHECK TO SEE IF YOU SHOULD ENTER A POSITION
    for symbol in tradesdf[tradesdf.open_trade == False].symbol:
        indicators_dict[symbol] = getminutedata(symbol, '5m', '2000', client)
        indicators_dict[symbol]  = applyindicators(indicators_dict[symbol] )
        indicators_dict[symbol]  = conditions(indicators_dict[symbol] ,strategy)
        #get the last row that has a full candelstick ie dont make decisions on incomplete candelsticks
        lastcompleterow = indicators_dict[symbol].iloc[-2]
        print(lastrow)
        if (lastcompleterow.Buy.values[0]==1)&(lastcompleterow.Sell.values[0]==0):
            buy_order = buy(symbol,investment,client,tradesdf)
        else:
            buy_order = None
    return tradesdf, tsl_dicts, indicators_dict
        
            
            
    
    
#%% Get my current trades i have made so i can find my profit margins
#Get a data frame with all information for buy and sell for my account
def Get_trades_df_fake_account(symbol,client):
    df = pd.DataFrame(client.get_my_trades(symbol = symbol))
    df['time'] = pd.to_datetime(df['time'],unit = 'ms')
    df['time_local'] = df['time']-pd.Timedelta(hours = 6)
    df['quoteQty'] = df['quoteQty'].astype(float)
    df2 = df.groupby(['orderId','time','time_local','commissionAsset','isBuyer','price'])['quoteQty'].sum().to_frame('Total_trade').reset_index()
    df2['Price_delta'] = np.where(df2['isBuyer']==True,-1.00075,.99925)*df2['Total_trade']
    df2['cumsum'] = df2['Price_delta'].cumsum()
    return df2

def Get_trades_df_real_account(symbol,client):
    df = pd.DataFrame(client.get_my_trades(symbol = symbol))
    df['time'] = pd.to_datetime(df['time'],unit = 'ms')
    df['time_local'] = df['time']-pd.Timedelta(hours = 6)
    df['quoteQty'] = df['quoteQty'].astype(float)
    df2 = df.groupby(['orderId','time','time_local','commissionAsset','isBuyer','price'])['quoteQty'].sum().to_frame('Total_trade').reset_index()
    df2['Price_delta'] = np.where(df2['isBuyer']==True,-1,1)*df2['Total_trade']
    df2['cumsum'] = df2['Price_delta'].cumsum()
    return df2


#%% Plot all the symbols
#needs to have some baseline subset of columns always so it is easier to plot
def Plot_all_symbols(indicators_dict,symbols):
    for symbol in symbols:
        plt.plot(indicators_dict[symbol][['Close','SMA_13','SMA_MAX','Upper_20_std','Lower_20_std']])
        plt.title(symbol)
        plt.show()
        
def Plot_all_symbols_chan(indicators_dict,symbols):
    for symbol in symbols:
        plt.plot(indicators_dict[symbol][['Close','EMA_100','Chan_Short','Chan_Long']])
        plt.title(symbol)
        plt.show()       
        
        
        
        
#%% Archive Functions
 #Need to update this to the new version I have on my backtesting stuff. 
# def applyindicators(df):
#     slope_lookback = 5
    
#     heikin = True
#     if heikin:
#         df2 = df.copy()
#         CloseH = 1/4*(df.Open+df.High+df.Low+df.Close)
#         OpenH = 1/2*(df.Open.shift()+df.Close.shift())
#         HighH = df[['High','Open','Close']].max(axis = 1)
#         LowH = df[['Low','Open','Close']].min(axis = 1)
#         df2.Close = CloseH
#         df2.Open = OpenH
#         df2.High= HighH
#         df2.Low = LowH
    
    
#     #SMA indicators
#     df['SMA_MAX'] = df.Close.rolling(150).mean()
#     df['SMA_MAX_slope'] = df.SMA_MAX.diff(slope_lookback)/df.SMA_MAX
#     df['SMA_25'] = df.Close.rolling(25).mean()
#     df['SMA_25_slope'] = df.SMA_25.diff(slope_lookback)/slope_lookback
#     df['SMA_50']=df.Close.rolling(50).mean()
#     df['SMA_50_slope'] = df.SMA_50.diff(slope_lookback)/slope_lookback
#     df['SMA_100']=df.Close.rolling(100).mean()
#     df['SMA_100_slope'] = df.SMA_100.diff(slope_lookback)/slope_lookback
#     df['SMA_20'] = df.Close.rolling(20).mean()
#     df['SMA_5'] = df.Close.rolling(5).mean()
#     df['SMA_8'] = df.Close.rolling(8).mean()
#     df['SMA_13'] = df.Close.rolling(13).mean()
#     df['SMA_13_slope'] =df.SMA_13.diff(13)/13
#     df['SMA_5_slope'] = df.SMA_5.diff(5)/5
    
#     #EMA indicators
#     df['EMA_25'] = ta.trend.ema_indicator(df.Close,window = 25)
#     df['EMA_25_slope'] = (df.EMA_25.diff(slope_lookback)/slope_lookback)/df.Close*100
#     df['EMA_50'] = ta.trend.ema_indicator(df.Close,window = 50)
#     df['EMA_50_slope'] = df.EMA_50.diff(slope_lookback)/slope_lookback/df.Close*100
#     df['EMA_100'] = ta.trend.ema_indicator(df.Close,window = 100)
#     df['EMA_100_slope'] = df.EMA_100.diff(slope_lookback)/slope_lookback/df.Close*100
    
#     #Bollinger Bands
#     df['stddev_20'] = df.Close.rolling(20).std()
#     df['Upper_20_std'] = df.SMA_20+2*df.stddev_20
#     df['Lower_20_std'] = df.SMA_20-2*df.stddev_20
    
#     #Rsi indicators
#     df['rsi_2']= ta.momentum.rsi(df.Close,2)
#     df['rsi_9'] = ta.momentum.rsi(df.Close,9)
#     df['rsi_10']= ta.momentum.rsi(df.Close,10)
#     df['rsi_11']= ta.momentum.rsi(df.Close,11)
#     df['rsi_100'] = ta.momentum.rsi(df.Close,100)
#     df['rsi_25'] = ta.momentum.rsi(df.Close,25)
    
#     # MACD indicators and cross overs. 
#     df['macd'] = ta.trend.macd_diff(df.Close)
#     df['macd_signal'] = ta.trend.macd_signal(df.Close)
#     df['macd_above_signal'] = np.where(df.macd>df.macd_signal,1,0)
#     df['macd_cross_below'] = np.where(df.macd_above_signal.diff()==-1,1,0)
#     df['macd_cross_above'] = np.where(df.macd_above_signal.diff()==1,1,0)
    
    
#     #Other Strategies
#     # df['rollhigh'] = df.High.rolling(15).max()
#     # df['rolllow'] = df.Low.rolling(15).min()
#     # df['mid'] = (df.rollhigh+df.rolllow)/2
#     # df['highapproach'] = np.where(df.Close>df.rollhigh*0.996,1,0)
#     # df['close_above_mid'] = np.where(df.Close>df.mid,1,0)
#     # df['midcross'] = df.close_above_mid.diff()==1
#     # df['stochrsi'] = ta.momentum.stochrsi(df.Close,window = 10,smooth1 = 3,smooth2 = 3)   
    
#     chan_info = ta2.CHANDELIER(df2,short_period = 10,long_period = 10,k = 2)
#     df = pd.concat([df,chan_info],axis = 1,ignore_index = False)
#     df.rename(columns = {'Short.':'Chan_Short','Long.':'Chan_Long'},inplace = True)
    
#     return(df)
