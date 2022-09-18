from abc import ABC, abstractmethod
import pandas as pd

class BrokerClass(ABC):

    @abstractmethod
    def get_data(self, interval, lookback) -> pd.DataFrame:
        ...

    @abstractmethod
    def buy(self):
        ...

    @abstractmethod
    def sell(self):
        ...