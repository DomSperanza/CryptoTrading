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


#changing position
def changepos(symbol,order,tradesdf):
    if order['side']=='BUY':
        tradesdf.loc[tradesdf['symbol']==symbol,'open_trade']=True
        tradesdf.loc[tradesdf['symbol']==symbol,'quantity']=float(order['origQty'])
    else:
        tradesdf.loc[tradesdf['symbol']==symbol,'open_trade']=False
        tradesdf.loc[tradesdf['symbol']==symbol,'quantity']=0
        
        
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

#Need to update this to the new version I have on my backtesting stuff. 
def applyindicators(df):
    slope_lookback = 5
    
    heikin = True
    if heikin:
        df2 = df.copy()
        CloseH = 1/4*(df.Open+df.High+df.Low+df.Close)
        OpenH = 1/2*(df.Open.shift()+df.Close.shift())
        HighH = df[['High','Open','Close']].max(axis = 1)
        LowH = df[['Low','Open','Close']].min(axis = 1)
        df2.Close = CloseH
        df2.Open = OpenH
        df2.High= HighH
        df2.Low = LowH
    
    
    #SMA indicators
    df['SMA_MAX'] = df.Close.rolling(150).mean()
    df['SMA_MAX_slope'] = df.SMA_MAX.diff(slope_lookback)/df.SMA_MAX
    df['SMA_25'] = df.Close.rolling(25).mean()
    df['SMA_25_slope'] = df.SMA_25.diff(slope_lookback)/slope_lookback
    df['SMA_50']=df.Close.rolling(50).mean()
    df['SMA_50_slope'] = df.SMA_50.diff(slope_lookback)/slope_lookback
    df['SMA_100']=df.Close.rolling(100).mean()
    df['SMA_100_slope'] = df.SMA_100.diff(slope_lookback)/slope_lookback
    df['SMA_20'] = df.Close.rolling(20).mean()
    df['SMA_5'] = df.Close.rolling(5).mean()
    df['SMA_8'] = df.Close.rolling(8).mean()
    df['SMA_13'] = df.Close.rolling(13).mean()
    df['SMA_13_slope'] =df.SMA_13.diff(13)/13
    df['SMA_5_slope'] = df.SMA_5.diff(5)/5
    
    #EMA indicators
    df['EMA_25'] = ta.trend.ema_indicator(df.Close,window = 25)
    df['EMA_25_slope'] = (df.EMA_25.diff(slope_lookback)/slope_lookback)/df.Close*100
    df['EMA_50'] = ta.trend.ema_indicator(df.Close,window = 50)
    df['EMA_50_slope'] = df.EMA_50.diff(slope_lookback)/slope_lookback/df.Close*100
    df['EMA_100'] = ta.trend.ema_indicator(df.Close,window = 100)
    df['EMA_100_slope'] = df.EMA_100.diff(slope_lookback)/slope_lookback/df.Close*100
    
    #Bollinger Bands
    df['stddev_20'] = df.Close.rolling(20).std()
    df['Upper_20_std'] = df.SMA_20+2*df.stddev_20
    df['Lower_20_std'] = df.SMA_20-2*df.stddev_20
    
    #Rsi indicators
    df['rsi_2']= ta.momentum.rsi(df.Close,2)
    df['rsi_9'] = ta.momentum.rsi(df.Close,9)
    df['rsi_10']= ta.momentum.rsi(df.Close,10)
    df['rsi_11']= ta.momentum.rsi(df.Close,11)
    df['rsi_100'] = ta.momentum.rsi(df.Close,100)
    df['rsi_25'] = ta.momentum.rsi(df.Close,25)
    
    # MACD indicators and cross overs. 
    df['macd'] = ta.trend.macd_diff(df.Close)
    df['macd_signal'] = ta.trend.macd_signal(df.Close)
    df['macd_above_signal'] = np.where(df.macd>df.macd_signal,1,0)
    df['macd_cross_below'] = np.where(df.macd_above_signal.diff()==-1,1,0)
    df['macd_cross_above'] = np.where(df.macd_above_signal.diff()==1,1,0)
    
    
    #Other Strategies
    # df['rollhigh'] = df.High.rolling(15).max()
    # df['rolllow'] = df.Low.rolling(15).min()
    # df['mid'] = (df.rollhigh+df.rolllow)/2
    # df['highapproach'] = np.where(df.Close>df.rollhigh*0.996,1,0)
    # df['close_above_mid'] = np.where(df.Close>df.mid,1,0)
    # df['midcross'] = df.close_above_mid.diff()==1
    # df['stochrsi'] = ta.momentum.stochrsi(df.Close,window = 10,smooth1 = 3,smooth2 = 3)   
    
    chan_info = ta2.CHANDELIER(df2,short_period = 10,long_period = 10,k = 2)
    df = pd.concat([df,chan_info],axis = 1,ignore_index = False)
    df.rename(columns = {'Short.':'Chan_Short','Long.':'Chan_Long'},inplace = True)
    
    return(df)

#need to update based on what i have in backtesting
def conditions(df_indicators, strategy = 'basic'):
    if strategy == 'basic':
        df_indicators['Buy'] = np.where(((df_indicators.Close<df_indicators.Lower_20_std*1)&
                          (df_indicators.Close*1>df_indicators.SMA_MAX))&
                          ((df_indicators.rsi_2<10) & (df_indicators.rsi_10<20)),1,0) 
    
        df_indicators['Sell'] = np.where((df_indicators.rsi_10>80),1,0)
        
    elif strategy == 'StochRSI+ShortSMA':
        df_indicators['Buy'] = np.where(((df_indicators.Close>df_indicators.SMA_MAX) &
                                        (df_indicators.Close<df_indicators.SMA_13) &
                                        (df_indicators.SMA_5_slope>0) &
                                        (df_indicators.rsi_9<40)),1,0)
        
        df_indicators['Sell'] = np.where(((df_indicators.SMA_13_slope<0) &
                                        (df_indicators.rsi_9>70)),1,0)
        
    elif strategy == 'macd+shortSMA+rsi':
        df_indicators['Buy'] = np.where(((df_indicators.Close>df_indicators.SMA_MAX) &
                                        (df_indicators.Close<df_indicators.SMA_13) &
                                        (df_indicators.SMA_5_slope>0) &
                                        (df_indicators.macd<0.5)&
                                        (df_indicators.rsi_9<40)),1,0)
        
        df_indicators['Sell'] = np.where(((df_indicators.SMA_13_slope<0) &
                                          (df_indicators.rsi_9>70)&
                                        (df_indicators.macd>0.7)),1,0)
    elif strategy == 'short_long_EMA':
        df_indicators['Buy'] = np.where(((df_indicators.Close<df_indicators.EMA_25) &
                                         (df_indicators.Close>df_indicators.EMA_50) &
                                         (df_indicators.Close>df_indicators.EMA_100) &
                                         (df_indicators.EMA_25>df_indicators.EMA_50) &
                                         (df_indicators.EMA_50>df_indicators.EMA_100) &
                                         (df_indicators.EMA_25_slope>.01) &
                                         (df_indicators.EMA_50_slope>.0075) &
                                         (df_indicators.EMA_100>0.005)),1,0)
        
        df_indicators['Sell'] = np.where(df_indicators.Close<df_indicators.EMA_100*1.004,1,0)
    
    elif strategy == 'macd':
        df_indicators['Buy'] = np.where(((df_indicators.macd_above_signal==1)&
                                         (df_indicators.macd<0)&
                                         (df_indicators.macd_signal<0)&
                                         (df_indicators.Close>df_indicators.EMA_100)&
                                         (df_indicators.EMA_100_slope>0)),1,0)
        #never have a sell signal. Just use the stoploss and target profit. 
        df_indicators['Sell'] = np.where(df_indicators.Close>0,0,1)
        
        
    elif strategy == 'chan':
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
def tsl(symbol,client,df = pd.DataFrame()):
    if len(df)==0:
        df = pd.DataFrame(client.get_ticker(symbol = symbol),index = [0])
        df = df[['closeTime','lastPrice']]
        df.closeTime = pd.to_datetime(df.closeTime,unit = 'ms')
        df['lastPrice'] = float(df['lastPrice'])
        df['Benchmark'] = df['lastPrice'].cummax()
        df['TSL'] = df['Benchmark']*0.99
    else:
        df2 = pd.DataFrame(client.get_ticker(symbol = symbol),index = [0])
        df2 = df2[['closeTime','lastPrice']]
        df2.closeTime = pd.to_datetime(df2.closeTime,unit = 'ms')
        df2['lastPrice'] = float(df2['lastPrice'])
        df = pd.concat([df,df2])
        df['Benchmark'] = df['lastPrice'].cummax()
        df['TSL'] = df['Benchmark']*0.99
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
    indicators_dict ={}
    for symbol in tradesdf.symbol:
        indicators_dict[symbol] = pd.DataFrame()
    for symbol in tradesdf[tradesdf.open_trade == True].symbol:        
        indicators_dict[symbol] = getminutedata(symbol, '5m', '2000', client)
        indicators_dict[symbol]  = applyindicators(indicators_dict[symbol] )
        indicators_dict[symbol]  = conditions(indicators_dict[symbol] ,strategy)
        tsl_dicts[symbol] = tsl(symbol, client,df = tsl_dicts[symbol])
        lastrow = indicators_dict[symbol].tail(1)
        TSL_Sell = True in (tsl_dicts[symbol]['lastPrice']<tsl_dicts[symbol]['TSL']).values 
        # get the purchase order price and look to make a 2.5% profit on the trade if it gets that high
        target_profit = float(client.get_my_trades(symbol = symbol)[-1]['price'])*1.02

        if (((lastrow['Sell'].values[0]==1) & (lastrow['Close'].values[0]>target_profit))| (TSL_Sell == True)) and not client.get_open_orders(symbol = symbol):
            sell_order = sell(symbol,client,tradesdf)
            tsl_dicts[symbol] = pd.DataFrame()
        else:
            sell_order = order
        
    for symbol in tradesdf[tradesdf.open_trade == False].symbol:
        indicators_dict[symbol] = getminutedata(symbol, '5m', '2000', client)
        indicators_dict[symbol]  = applyindicators(indicators_dict[symbol] )
        indicators_dict[symbol]  = conditions(indicators_dict[symbol] ,strategy)
        lastrow = indicators_dict[symbol].tail(1)
        print(lastrow)
        if (lastrow.Buy.values[0]==1)&(lastrow.Sell.values[0]==0):
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