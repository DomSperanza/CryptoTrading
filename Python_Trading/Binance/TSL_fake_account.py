# -*- coding: utf-8 -*-
"""
Created on Tue May 31 16:05:08 2022

@author: dvspe
"""

import pandas as pd
import os
from binance.client import Client
import time
import matplotlib.pyplot as plt
from binance import ThreadedWebsocketManager


#change the directory to the correct one so that all the code refereces the correct spot
#This will only work on this computer
os.chdir(r'C:\Users\dvspe\Desktop\Python_Trading')

#import user functions
import Functions.Binance_Functions as func


#get the binance api keys to log onto the network and start pulling data
key = pd.read_csv('./Binance_Keys/binance_api_keys_testing.txt')
key = key.set_index('Type')
API_key = key. loc['API_key'].values[0]
Secret_key = key.loc['Secret_key'].values[0]

#set up the client for binance
client = Client(api_key =  API_key,api_secret = Secret_key,tld = 'us')
client.API_URL = 'https://testnet.binance.vision/api'
print(client.get_account())
print(client.get_asset_balance(asset = 'BTC'))
account_df = client.get_account()
account_df = pd.DataFrame(account_df['balances'])

#%%
price = {'ETHUSDT':pd.DataFrame(columns = ['date','price']),'error':False}
symbol = 'ETHUSDT'

def btc_pairs_trade(msg):
    if msg['e'] != 'error':
        price['ETHUSDT'].loc[len(price['ETHUSDT'])] = [pd.Timestamp.now(), float(msg['c'])]
    else:
        price['error'] = True
        
bsm = ThreadedWebsocketManager()
bsm.start()
time.sleep(1)
bsm.start_symbol_ticker_socket(callback = btc_pairs_trade, symbol = 'BTCUSDT')

## main
while len(price[symbol]) == 0:
	# wait for WebSocket to start streaming data
	time.sleep(0.1)
	
time.sleep(10)



#%%
btc_price = {'error':False}
def btc_trade_history(msg):
    ''' define how to process incoming WebSocket messages '''
    if msg['e'] != 'error':
        print(msg['c'])
        btc_price['last'] = msg['c']
        btc_price['bid'] = msg['b']
        btc_price['last'] = msg['a']
        btc_price['error'] = False
    else:
        btc_price['error'] = True
        
bsm = ThreadedWebsocketManager()
bsm.start()

bsm.start_symbol_ticker_socket(callback=btc_trade_history, symbol='BTCUSDT')
