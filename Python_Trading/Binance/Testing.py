

# -*- coding: utf-8 -*-
"""
Created on Tue May 24 11:33:24 2022

@author: dvspe

Purpose: Trading bot for Python useing Binance.US api
This script will be using the test account so no actual money will be used. 

"""
import pandas as pd
import os
from binance.client import Client


#change the directory to the correct one so that all the code refereces the correct spot
#This will only work on this computer
os.chdir(r'C:\Users\dvspe\Desktop\Python_Trading')

#get the binance api keys to log onto the network and start pulling data
key = pd.read_csv('./Binance_Keys/binance_api_keys_testing.txt')
key = key.set_index('Type')
API_key = key.loc['API_key'].values[0]
Secret_key = key.loc['Secret_key'].values[0]

#set up the client for binance
client = Client(api_key =  API_key,api_secret = Secret_key,tld = 'us')
client.API_URL = 'https://testnet.binance.vision/api'

print(client.get_account())
print(client.get_asset_balance(asset = 'BTC'))
account_df = client.get_account()
account_df = pd.DataFrame(account_df['balances'])



#creating a test order for this account
buy_order_market = client.create_order(
    symbol = 'ETHUSDT',
    side = 'BUY',
    type = 'MARKET',
    quantity = 1)

account_df = client.get_account()
account_df = pd.DataFrame(account_df['balances'])
sell_order_market = client.order_market_sell(
    symbol = 'ETHUSDT',
    quantity = float(account_df[account_df['asset']=='ETH']['free'].values[0]))

account_df = client.get_account()
account_df = pd.DataFrame(account_df['balances'])

#get the account total USDT value
assets = account_df['asset'].unique()
symbols = []
USDT_value = []
for asset in assets:
    if asset !='USDT':
        client.get_asset_balance(asset = asset)
