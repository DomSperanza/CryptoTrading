# -*- coding: utf-8 -*-
"""
Created on Thu May 26 13:26:00 2022

@author: dvspe



"""

import pandas as pd
import os
from binance.client import Client
import time
import matplotlib.pyplot as plt
from sqlalchemy import create_engine



#change the directory to the correct one so that all the code refereces the correct spot
#This will only work on this computer
os.chdir(r'C:\Users\dvspe\Desktop\Python_Trading')

#import user functions
import Functions.Binance_Functions as func

#%% Connects to the Database Engine
engine = create_engine('sqlite:///Binance/SQL_Engine/Live_Crypto_Data.db')
df_TSL = pd.read_sql('ETHUSDT',engine)

#%%
#get the binance api keys to log onto the network and start pulling data
key = pd.read_csv('./Binance_Keys/binance_api_keys_testing.txt')
key = key.set_index('Type')
API_key = key.loc['API_key'].values[0]
Secret_key = key.loc['Secret_key'].values[0]

#set up the client for binance
client = Client(api_key =  API_key,api_secret = Secret_key,tld = 'us')
client.API_URL = 'https://testnet.binance.vision/api'
print(client.get_account())
account_df = client.get_account()
account_df = pd.DataFrame(account_df['balances'])

Starting_Amount = float(account_df[account_df.asset == 'USDT']['free'].values[0])

#%% Make a tradesdf
symbols = ['ETHUSDT']
tradesdf = pd.DataFrame({'symbol':symbols})
tradesdf['open_trade']=False
tradesdf['quantity']= 0
order = None

#%% make the getminute data DF for eth
df_indicators = func.getminutedata('ETHUSDT',client)

df_indicators = func.applyindicators(df_indicators)

#visualize dataframe
plt.plot(df_indicators[['Close','SMA_20','Upper','Lower']])
plt.show()
#acts as a counter for making plots
i = 0
#%%Add in buying and selling indicators column
#func.conditions(df)

#%% Make a buy limit order
 #-> needs a price quanity
 # -> both need to be calculated

while True:
    time.sleep(5)
    
    #should make a plot with the df_indicators ever
    if (i%360==0):
        #visualize dataframe
        plt.plot(df_indicators[['Close','SMA_20','Upper','Lower']])
        plt.show()
    i = i+1
    print(tradesdf[tradesdf.open_trade==True].symbol)
    try:
        df_indicators,order,tradesdf= func.trader(1000,client,tradesdf,engine, order)
        account_df = client.get_account()
        account_df = pd.DataFrame(account_df['balances'])
        print(client.get_symbol_ticker(symbol = 'ETHUSDT'))
        print('RSI: '+ str(df_indicators['rsi'][-1]))
        print('Close: ' +str(df_indicators['Close'][-1]) +'   SMA_200: '+str(df_indicators['SMA_200'][-1])+'   Lower: '+str(df_indicators['Lower'][-1]))
        
    except KeyboardInterrupt:
        break
    except: 
        continue