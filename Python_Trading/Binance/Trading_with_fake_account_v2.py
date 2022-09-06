# -*- coding: utf-8 -*-
"""
Created on Sun Jun 19 18:24:06 2022

@author: dvspe
"""

import Functions.Binance_Functions_v2 as func
import pandas as pd
import os
from binance.client import Client
import time
import matplotlib.pyplot as plt
from dotenv import load_dotenv


# should work ony any computer
path, filename = os.path.split(os.path.realpath(__file__))
# should got to Python_Trading AKA one directory up from current file's directory
os.chdir(path+"\..")

# change the directory to the correct one so that all the code refereces the correct spot
# This will only work on this computer
# os.chdir(r'C:\Users\dvspe\Desktop\Python_Trading')

# import user functions

# %% Connects to the Database Engine
#engine = create_engine('sqlite:///Binance/SQL_Engine/Live_Crypto_Data.db')
#df_TSL = pd.read_sql('ETHUSDT',engine)

# %%
# get the binance api keys to log onto the network and start pulling data
# key = pd.read_csv('./Binance_Keys/binance_api_keys_testing.txt')
# key = key.set_index('Type')
# API_key = key.loc['API_key'].values[0]
# Secret_key = key.loc['Secret_key'].values[0]

# new format
load_dotenv()

# env constant names
key_var = 'BINANCE_API'
secret_var = 'BINANCE_SECRET'

# assign desired API keys
API_key = os.getenv(key_var)
Secret_key = os.getenv(secret_var)


# set up the client for binance
client = Client(api_key=API_key, api_secret=Secret_key, tld='us')
client.API_URL = 'https://testnet.binance.vision/api'
print(client.get_account())
account_df = client.get_account()
account_df = pd.DataFrame(account_df['balances'])

Starting_Amount = float(
    account_df[account_df.asset == 'USDT']['free'].values[0])

# %% Make a tradesdf
symbols = ['BNBUSDT', 'BTCUSDT']
tradesdf = pd.DataFrame({'symbol': symbols})
tradesdf['open_trade'] = False
tradesdf['quantity'] = 0
order = None


# %% Set Trading Stratgy
strategy = 'chan'

# %% Get the oringial indicators_dictionaries.
indicators_dict = {}
for symbol in tradesdf.symbol:
    indicators_dict[symbol] = pd.DataFrame()
    indicators_dict[symbol] = func.getminutedata(symbol, '5m', '2000', client)
    indicators_dict[symbol] = func.applyindicators(indicators_dict[symbol])
    indicators_dict[symbol] = func.conditions(
        indicators_dict[symbol], strategy)

# %% Set up the tsl dataframes for when a buy order is triggered
tsl_dicts = {}
for symbol in symbols:
    tsl_dicts[symbol] = pd.DataFrame()

# %% Makes initial plots of the data to examin if i want to start trading
func.Plot_all_symbols(indicators_dict, symbols)
i = 0

# %% Make a buy limit order
# -> needs a price quanity
# -> both need to be calculated

while True:
    time.sleep(30)

    # should make a plot with the df_indicators ever
    if (i % 360 == 0):
        # visualize dataframe
        func.Plot_all_symbols(indicators_dict, symbols)
    i = i+1
    print(tradesdf[tradesdf.open_trade == True].symbol)
    try:
        tradesdf, tsl_dicts, indicators_dict = func.trader(
            1000, client, tradesdf, tsl_dicts, strategy, order)
        account_df = client.get_account()
        account_df = pd.DataFrame(account_df['balances'])
        for symbol in symbols:
            print(client.get_symbol_ticker(symbol=symbol))
            if len(tsl_dicts[symbol]) > 0:
                print(tsl_dicts[symbol]
                      [['lastPrice', 'Benchmark', 'TSL']].tail(5))
    except KeyboardInterrupt:
        break
    except:
        continue
