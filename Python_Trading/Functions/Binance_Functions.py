# -*- coding: utf-8 -*-
"""
Created on Thu May 26 12:37:33 2022

@author: dvspe
Purpose:
    Keep all of the Binance functions accessable for creating scripts
    
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

#Get total account value for test
def get_account_value_testing():
    return




#changing position
def changepos(symbol,order,tradesdf):
    if order['side']=='BUY':
        tradesdf.loc[tradesdf['symbol']==symbol,'open_trade']=True
        tradesdf.loc[tradesdf['symbol']==symbol,'quantity']=float(order['origQty'])
    else:
        tradesdf.loc[tradesdf['symbol']==symbol,'open_trade']=False
        tradesdf.loc[tradesdf['symbol']==symbol,'quantity']=0
        
def getminutedata(symbol,client):
    frame = pd.DataFrame(client.get_historical_klines(symbol,
                                                      '1m',
                                                      '200 minutes ago UTC'))
    frame = frame[[0,4]]
    frame.columns = ['Time','Close']
    frame.set_index('Time',inplace = True)
    frame.index = pd.to_datetime(frame.index,unit = 'ms')
    frame.Close = frame.astype(float)
    z_scores = zscore(frame)
    abs_z_scores = np.abs(z_scores)
    filtered_entries = (abs_z_scores < 3).all(axis=1)
    frame = frame[filtered_entries]
    return frame

#add several indicators to your dataframe. 
def applyindicators(df):
    df['SMA_200'] = df.Close.rolling(len(df)).mean()
    df['SMA_20'] = df.Close.rolling(20).mean()
    df['stddev'] = df.Close.rolling(20).std()
    df['Upper'] = df.SMA_20+2*df.stddev
    df['Lower'] = df.SMA_20-2*df.stddev
    df['rsi'] = ta.momentum.rsi(df.Close,2)
    return(df)
    

#%%Set the conditions for buying and selling indicators
def conditions(df_indicators):
    df_indicators['Buy'] = np.where(((df_indicators.Close<df_indicators.Lower*1)&
                          (df_indicators.Close*1>df_indicators.SMA_200))|
                          (df_indicators.rsi<2),1,0)
    
    df_indicators['Sell'] = np.where((df_indicators.rsi>40),1,0)
    return(df_indicators)
    

    

def get_live_stream(engine,order = None):
    
    if order != None:
        df_TSL = pd.read_sql(f"""SELECT * FROM ETHUSDT WHERE \
                             Time_Stamp>='{pd.to_datetime(order['transactTime'],unit ='ms')}'""",engine)
        df_TSL['Benchmark'] = df_TSL['price'].cummax()
        df_TSL['TSL'] = df_TSL['Benchmark']*0.99
    else:
        df_TSL = pd.DataFrame(columns = ['Time_Stamp','price','Benchmark','TSL'])
    return(df_TSL)

#%% MAKES SURE ORDER IS NOT GOING TO PRODUCE AN ERROR   
#Function to get the limit order price that is properly rounded. 
def pricecalc(symbol,client, limit = 1):
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
        type = 'MARKET',quantity = tradesdf[tradesdf['symbol']==symbol]['quantity'].values[0])
    changepos(symbol,order,tradesdf)
    print(order)
    return(order)
    


#%%
#make our traders. Will continue until all money is gone
def trader(investment,client,tradesdf,engine,order = None):
    #selling conditions
    for symbol in tradesdf[tradesdf['open_trade']==True]['symbol']:
        
        #get the indicators dataframe
        df_indicators = getminutedata(symbol,client)
        df_indicators = applyindicators(df_indicators)
        df_indicators = conditions(df_indicators)
        
        
        df_TSL = get_live_stream(engine,order)
       
        lastrow = df_indicators.tail(1)
        print(df_TSL.tail(10))
        TSL_Sell = True in (df_TSL['price']<df_TSL['TSL']).values 
        #define when you want to sell 
        if lastrow['Sell'].values[0]==1 and TSL_Sell == True and not client.get_open_orders(symbol = symbol):
            sell_order = sell(symbol,client,tradesdf)
        else:
            sell_order = order
        return df_indicators,sell_order,tradesdf
    for symbol in tradesdf[tradesdf['open_trade']==False]['symbol']:
        df_indicators = getminutedata(symbol, client)
        applyindicators(df_indicators)
        conditions(df_indicators)
        lastrow = df_indicators.tail(1)
        if lastrow['Buy'].values[0]==1:
            buy_order = buy(symbol,investment,client,tradesdf)
        else:
            buy_order = None
        return df_indicators,buy_order,tradesdf
        
    
#Get a data frame with all information for buy and sell for my account
def Get_trades_df (symbol,client):
    df = pd.DataFrame(client.get_my_trades(symbol = symbol))
    df['time'] = pd.to_datetime(df['time'],unit = 'ms')
    df['quoteQty'] = df['quoteQty'].astype(float)
    df = df.groupby(['orderId','time','commissionAsset','isBuyer'])['quoteQty'].sum().to_frame('Total_trade').reset_index()
    df['Price_delta'] = np.where(df['isBuyer']==True,-1.001,.999)*df['Total_trade']
    return df

        

    