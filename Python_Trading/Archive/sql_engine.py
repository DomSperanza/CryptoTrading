# -*- coding: utf-8 -*-
"""
Created on Mon May 30 12:37:49 2022

@author: dvspe
purpose: to get a live sql query to get stuff working a bit. 
"""

import pandas as pd
import os
from binance.client import Client
import time
import matplotlib.pyplot as plt
import sqlalchemy
from binance import BinanceSocketManager
import websocket,json


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
#this changes so i am using my test account
client.API_URL = 'https://testnet.binance.vision/api'

symbol = 'ETHUSDT'


engine = sqlalchemy.create_engine('sqlite:///CryptoDB.db')
stream = "wss.//stream.binance.com:9443/we/!miniTicker@arr"

def on_message(ws,message):
    msg = json.loads(message)
    symbol = [x for x in msg if x['s'].endswith('USDT')]
    frame = pd.DataFrame(symbol)[['E','s','c']]
    frame.E = pd.to_datetime(frame.E,unit = "ms")
    frame.c = frame.c.astype(float)
    for row in range(len(frame)):
        data = frame[row:row+1]
        data[['E','c']].to_sql(data['s'].values[0],engine,index = False, if_exists = 'append')
        
    
ws = websocket.WebSocketApp(stream,on_message = on_message)
ws.run_forever()

while True:
    await socket.__aenter__()
    