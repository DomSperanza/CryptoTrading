from ibapi.contract import Contract

# TODO: create a valid symbols file
stocks = ["SPY"]

cryptos = ["BTC"]

class IBContract(Contract):
    def __init__(self, symbol: str):
        Contract.__init__(self)    

        self.symbol = symbol
        self.currency = "USD"

        if symbol in stocks:
            self.secType = "STK"
            self.exchange = "SMART"
        elif symbol in cryptos:
            self.secType = "CRYPTO"
            self.exchange = "PAXOS"
        else:
            raise ValueError("Not an accepted symbol")