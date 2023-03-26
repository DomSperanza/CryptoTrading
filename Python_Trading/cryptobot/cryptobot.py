from http import client
import os
path, filename = os.path.split(os.path.realpath(__file__))
# should got to Python_Trading AKA one directory up from current file's directory
os.chdir(path+"\..")
from dotenv import load_dotenv
import pandas as pd
import strategies as st
import brokers as br
from binance.client import Client
#%%

STOCKS = ['SPY','DIA']
CRYPTOS = ['BNBUSDT', 'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'DOGEUSDT']

# # loads in environment variables from .env file
# load_dotenv()

# # assign desired API keys
# api_key = os.getenv('BINANCE_PAPER_API')
# api_secret = os.getenv('BINANCE_PAPER_SECRET')

strategy = st.Heiken_EMA
broker = br.Binance

class CryptoBot(strategy,broker):
    '''
    Activates the cryptobot to begin trading based on a given strategy.

    Parameters:
    symbol : str
        The symbol of the crypto to be traded

    Inherited:
    df : pd.Dataframe
        Dataframe of the 
    '''

    def __init__(self, symbol, **kwargs):
        # inherits all methods from the passed strategy and broker
        strategy.__init__(self, **kwargs)
        broker.__init__(self, symbol, **kwargs)

        self.symbol = symbol

    def run_backtest(self, interval:str = '1m', lookback:str = '400'):
        self.get_data(interval,lookback)
        self.apply_indicators()
        self.apply_strat()
        #self.plot_visual_plotly()
        return self.trades_stats()
#%%
#backtest
strat_log = dict()
for symbol in ['ETHUSDT']:
    strat_log[symbol] = dict()
    bot = CryptoBot(symbol)
    stats = bot.run_backtest(interval = '5m',lookback = '100')
    strat_log[symbol] = stats
    print(stats)
    # print(bot.df.head(),'\n',bot.df.tail())
my_df = bot.df
my_trades = bot.trades_df
