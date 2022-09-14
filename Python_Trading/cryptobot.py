import os
from dotenv import load_dotenv
import math


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from binance.client import Client

from strategies.strategy import *


brokers = ['binance','ibkr']
stocks = ['SPY','DIA']
cryptos = ['BTCUSDT']

class CryptoBot:
    '''
    Activates the cryptobot to begin trading based on a given strategy.
    For now, will just work in Binance.

    Parameters:
    symbol : str
        The symbol of the crypto to be traded
    strategy : str
        The strategy to be implemented
    '''

    def __init__(self, 
                symbol: str, 
                strategy: Strategy,
                client: Client = Client(),
                df: pd.DataFrame = None,
                broker: str = 'binance') -> None:

        # validity checks (currently restricting symbols)
        if broker not in brokers:
            raise ValueError(f"Invalid Broker: {broker}")
        if symbol not in cryptos:
            raise ValueError(f"Invalid Symbol: {symbol}")

        self.symbol = symbol
        self.strategy = strategy
        self.client = client
        self.df = df
        self.broker = broker

        

    def getdata(self, interval: str ='1m', lookback: str ='400'):
        frame = pd.DataFrame(self.client.get_historical_klines(self.symbol,
                                                        interval,
                                                        lookback + ' hours ago UTC'))
        frame = frame.iloc[:, 0:6]
        frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        frame.set_index('Time', inplace=True)
        frame.index = pd.to_datetime(frame.index, unit='ms')
        frame = frame.astype(float)
        self.df = frame
        return self.df



if __name__ == '__main__':

    # loads in environment variables from .env file
    load_dotenv()

    # assign desired API keys
    api_key = os.getenv('BINANCE_PAPER_API')
    api_secret = os.getenv('BINANCE_PAPER_SECRET')

    # client = Client(api_key, api_secret,testnet=True)

    # run bot with user inputs
    bot = CryptoBot("BTCUSDT", Strategy)
    data = bot.getdata(lookback='100')
    print(data.head(),'\n',data.tail())
