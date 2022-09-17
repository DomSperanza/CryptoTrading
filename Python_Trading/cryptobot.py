import os
from dotenv import load_dotenv
import pandas as pd
import strategies as st
import brokers as br
from binance.client import Client


STOCKS = ['SPY','DIA']
CRYPTOS = ['BNBUSDT', 'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'DOGEUSDT']

# # loads in environment variables from .env file
# load_dotenv()

# # assign desired API keys
# api_key = os.getenv('BINANCE_PAPER_API')
# api_secret = os.getenv('BINANCE_PAPER_SECRET')

strategy = st.HighLow
broker = br.Binance

class CryptoBot(strategy,broker):
    '''
    Activates the cryptobot to begin trading based on a given strategy.

    Parameters:
    symbol : str
        The symbol of the crypto to be traded
    '''

    def __init__(self, symbol: str, client = Client()):
        # inherits all methods from the passed strategy and broker
        strategy(self).__init__
        broker(self).__init__
        self.df = pd.DataFrame
        self.symbol = symbol
        self.trades_df = pd.DataFrame
        self.client = client


strat_log = dict()
for symbol in ['BTCUSDT']:
    strat_log[symbol] = dict()
    bot = CryptoBot(symbol)
    bot.get_data(lookback='100')
    print(bot.df.head(),'\n',bot.df.tail())
