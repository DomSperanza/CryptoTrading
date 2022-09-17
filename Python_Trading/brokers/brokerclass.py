from abc import ABC, abstractmethod
import pandas as pd

class BrokerClass(ABC):

    # @abstractmethod
    # def __init__(self):
    #     ...

    @abstractmethod
    def get_data(self) -> pd.DataFrame:
        ...

    @abstractmethod
    def buy(self):
        ...

    @abstractmethod
    def sell(self):
        ...