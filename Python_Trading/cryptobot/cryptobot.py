from http import client
import os
#path, filename = os.path.split(os.path.realpath(__file__))
# should got to Python_Trading AKA one directory up from current file's directory
#os.chdir(path+"\..")
from dotenv import load_dotenv
import pandas as pd
import strategies as st
import brokers as br
from binance.client import Client
#%%

#STOCKS = ['SPY','DIA']
#CRYPTOS = ['BNBUSDT', 'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'DOGEUSDT']

# # loads in environment variables from .env file
# load_dotenv()

# # assign desired API keys
# api_key = os.getenv('BINANCE_PAPER_API')
# api_secret = os.getenv('BINANCE_PAPER_SECRET')



class CryptoBot:
    '''
    Activates the cryptobot to begin trading based on a given strategy.
    Parameters:
    symbol : str
        The symbol of the crypto to be traded
    Inherited:
    df : pd.Dataframe
        Dataframe of the 
    '''

    def __init__(self, symbol, broker_class, strategy_class=None, **kwargs):
        # inherits all methods from the passed strategy and broker
        self.broker = broker_class(symbol, **kwargs)
        if strategy_class is not None:
            self.strategy = strategy_class(**kwargs)
        else:
            self.strategy = None

        self.symbol = symbol

    def get_test_data(self,interval, lookback):
        return self.broker.get_data(interval,lookback)

    def test_strat(self):
        if self.strategy is not None:
            self.strategy.apply_indicators()
            self.strategy.apply_strat()
            return self.strategy.trades_stats()
        else:
            raise ValueError("No strategy selected")

    def run_backtest(self, interval:str = '1m', lookback:str = '400'):
        if self.strategy is not None:
            self.strategy.df = self.broker.get_data(interval,lookback)
            self.strategy.apply_indicators()
            self.strategy.apply_strat()
            #self.plot_visual_plotly()
            return self.strategy.trades_stats()
        else:
            raise ValueError("No strategy selected")
#%%
#backtest
if __name__== '__main__':
    strat = st.HighLow
    broker = br.Binance
    strat_log = dict()
    for symbol in ['ETHUSDT']:
        strat_log[symbol] = dict()
        bot = CryptoBot(symbol = symbol, broker_class = broker,strategy_class=strat)
        stats = bot.run_backtest(interval = '5m',lookback = '100')
        strat_log[symbol] = stats
        print(stats)
        # print(bot.df.head(),'\n',bot.df.tail())

