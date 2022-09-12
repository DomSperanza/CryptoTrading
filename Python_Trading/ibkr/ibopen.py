# https://levelup.gitconnected.com/executing-orders-on-interactive-brokers-api-how-to-guide-b8fb6059a0f0

from ibdataapp import IBDataApp
import time
import pandas as pd

from ibcontract import IBContract
from ibapi.order import Order

# from enum import Enum
# class OrderAction(str, Enum):
#     BUY="BUY"
#     SELL="SELL"

# class OrderType(str, Enum):
#     MKT = "MKT"
#     LIMIT="LMT"
#     MID = "MIDPRICE"

if __name__ == "__main__":

    app = IBDataApp("localhost", 7497, 0)

    time.sleep(2)

    contract = IBContract("SPY")

    order = Order()
    # order.action = OrderAction.BUY
    # order.orderType = OrderType.MKT
    order.action = "BUY"
    order.orderType = "MKT"
    order.totalQuantity = 1
    # order.cashQty = 22302
    # order.tif = "IOC"
    order.transmit = True


    app.placeOrder(
        app.nextValidOrderId,
        contract, 
        order
    )


    time.sleep(4)
    app.disconnect()
