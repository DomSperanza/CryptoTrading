# -*- coding: utf-8 -*-
"""
Created on Tue May 24 11:33:24 2022

@author: dvspe

Purpose: Trading bot for Python useing Binance.US api

"""
import pandas as pd
import os
from binance.client import Client


#change the directory to the correct one so that all the code refereces the correct spot
#This will only work on this computer
os.chdir(r'C:\Users\dvspe\Desktop\Python_Trading')

#get the binance api keys to log onto the network and start pulling data
key = pd.read_csv('./Binance_Keys/binance_api_keys.txt')
key = key.set_index('Type')
API_key = key.loc['API_key'].values[0]
Secret_key = key.loc['Secret_key'].values[0]

#set up the client for binance
client = Client(api_key =  API_key,api_secret = Secret_key,tld = 'us')





