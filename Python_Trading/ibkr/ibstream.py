from ibdataapp import IBDataApp
import time
import pandas as pd

from ibapi.contract import Contract


if __name__ == "__main__":

    
    app = IBDataApp("localhost", 7497, 0)

    time.sleep(2)

    contract = Contract()
    # contract.symbol = "SPY"
    # contract.secType = "STK"
    # contract.currency = "USD"
    # contract.exchange = "SMART"

    contract.symbol = "BTC"
    contract.secType = "CRYPTO"
    contract.currency = "USD"
    contract.exchange = "PAXOS"

    reqId = app.reqTickByTickData(
        1001,
        contract,
        "BidAsk",
        0,
        False
    )

    # reqId = app.reqMktData(
    #     1001,
    #     contract,
    #     "",``
    #     False, # snapshot (True) or stream (False)
    #     False, #ALWAYS MAKE SURE THIS IS FALSE (0.01USD cost per rqst)
    #     []
    # )

    time.sleep(12)

    app.disconnect()
