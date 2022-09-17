from .brokerclass import BrokerClass
import pandas as pd
from binance.client import Client


class Binance(BrokerClass):
    '''
    Instantiates an empty client by default.
    For now, pass in Client with key/secret for full func.
    '''

    def __init__(self, 
                client: Client = Client()):
        BrokerClass.__init__
        self.client = client

    def get_data(self, interval: str ='1m', lookback: str ='400') -> pd.DataFrame:
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

    def buy(self):
        pass

    def sell(self):
        pass
    