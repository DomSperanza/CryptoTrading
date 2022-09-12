# https://github.com/IbcAlpha/IBC
# https://blog.devgenius.io/interactive-brokers-api-for-python-d53eb80cc2b9

from ibapi.client import EClient
from ibapi.wrapper import EWrapper, TickAttrib, TickerId, TickAttribBidAsk
from ibapi.ticktype import TickTypeEnum, TickType
from ibapi.utils import floatMaxString, Decimal, decimalMaxString, logging

from threading import Thread
import queue

from dateutil import parser

from datetime import datetime

import pandas as pd


class IBDataApp(EWrapper, EClient):
    def __init__(self, host, port, clientId):
        EWrapper.__init__(self)
        EClient.__init__(self, self)

        self.data_queue_dict = {}
        self.datetime_list = list()
        self.open_list = list()
        self.high_list = list()
        self.low_list = list()
        self.close_list = list()
        self.volume_list = list()

        self.connect(host=host, port=port, clientId=clientId)

        thread = Thread(target=self.run)
        thread.start()
        setattr(self, "_thread", thread)

    # def nextValidId(self, orderId):

    #     print("Connection successful. Connection time: %s, Next valid Id: %d" % (
    #         self.twsConnectionTime().decode("ascii"), orderId
    #     ))

    def nextValidId(self, orderId: int):
             super().nextValidId(orderId)
    
             logging.debug("setting nextValidOrderId: %d", orderId)
             self.nextValidOrderId = orderId
             print("NextValidId:", orderId)

    def tickPrice(self, reqId: TickerId, tickType: TickType, price: float, attrib: TickAttrib):
        super().tickPrice(reqId, tickType, price, attrib)
        print("TickPrice. TickerId:", reqId, "tickType:", tickType,
                "Price:", floatMaxString(price), "CanAutoExecute:", attrib.canAutoExecute,
                "PastLimit:", attrib.pastLimit, end=' ')
        if tickType == TickTypeEnum.BID or tickType == TickTypeEnum.ASK:
            print("PreOpen:", attrib.preOpen)
        else:
            print()

    def tickByTickBidAsk(self, reqId: int, time: int, bidPrice: float, askPrice: float,
                         bidSize: Decimal, askSize: Decimal, tickAttribBidAsk: TickAttribBidAsk):
        super().tickByTickBidAsk(reqId, time, bidPrice, askPrice, bidSize,
                                 askSize, tickAttribBidAsk)
        print("BidAsk. ReqId:", reqId,
              "Time:", datetime.fromtimestamp(time).strftime("%Y%m%d-%H:%M:%S"),
              "BidPrice:", floatMaxString(bidPrice), "AskPrice:", floatMaxString(askPrice), "BidSize:", decimalMaxString(bidSize),
              "AskSize:", decimalMaxString(askSize), "BidPastLow:", tickAttribBidAsk.bidPastLow, "AskPastHigh:", tickAttribBidAsk.askPastHigh)


    # def tickSize(self, reqId: TickerId, tickType: TickType, size: Decimal):
    #     super().tickSize(reqId, tickType, size)
    #     print("TickSize. TickerId:", reqId, "TickType:", tickType, "Size: ", decimalMaxString(size))

    # def tickString(self, reqId: TickerId, tickType: TickType, value: str):
    #     super().tickString(reqId, tickType, value)
    #     print("TickString. TickerId:", reqId, "Type:", tickType, "Value:", value)

    # def tickGeneric(self, reqId: TickerId, tickType: TickType, value: float):
    #     super().tickGeneric(reqId, tickType, value)
    #     print("TickGeneric. TickerId:", reqId, "TickType:", tickType, "Value:", floatMaxString(value))

    def tickSnapshotEnd(self, reqId: int):
        super().tickSnapshotEnd(reqId)
        print("TickSnapshotEnd. TickerId:", reqId)
        
    def historicalData(self, reqId, bar):
        self.data_queue_dict[reqId].put(bar)

    def historicalDataEnd(self, reqId, start, end):

        print(f"Finished receiving current batch of historical data. Start: {start}. End: {end}")

        while not self.data_queue_dict[reqId].empty():

            bar_data = self.data_queue_dict[reqId].get()

            # ! change this conversion to work as a dataframe
            # self.datetime_list.append(parser.parse(bar_data.date, ignoretz=True))
            self.datetime_list.append(bar_data.date)
            self.open_list.append(bar_data.open)
            self.high_list.append(bar_data.high)
            self.low_list.append(bar_data.low)
            self.close_list.append(bar_data.close)
            self.volume_list.append(bar_data.volume)

    def request_historical_data(self, reqId, contract, endDateTime, durationStr, barSizeSetting, whatToShow,
                                useRTH, formatDate, keepUpToDate):

        print(f"Requesting historical data for {contract.symbol} at {contract.exchange}")

        self.reqHistoricalData(
            reqId=reqId,
            contract=contract,
            endDateTime=endDateTime,
            durationStr=durationStr,
            barSizeSetting=barSizeSetting,
            whatToShow=whatToShow,
            useRTH=useRTH,
            formatDate=formatDate,
            keepUpToDate=keepUpToDate,
            chartOptions=[]
        )

        if reqId not in self.data_queue_dict.keys():

            print("Setting up queue for reqId %d" % reqId)
            self.data_queue_dict[reqId] = queue.Queue()

        return reqId

    def data_to_dataframe(self):

        data = {
            "open": self.open_list,
            "high": self.high_list,
            "low": self.low_list,
            "close": self.close_list,
            "volume": self.volume_list
        }

        dataframe = pd.DataFrame(data, index=self.datetime_list)
        dataframe.sort_index(inplace=True)

        return dataframe


# if __name__ == "__main__":

#     app = IBDataApp("localhost", 7497, 0)

#     time.sleep(2)

#     contract = Contract()
#     # contract.symbol = "SPY"
#     # contract.secType = "STK"
#     # contract.currency = "USD"
#     # contract.exchange = "SMART"

#     contract.symbol = "BTC"
#     contract.secType = "CRYPTO"
#     contract.currency = "USD"
#     contract.exchange = "PAXOS"

#     # note Timezone
#     dt_range = pd.date_range(start="20220328 23:59:59", end="20220401 23:59:59", freq="24H")

#     for dt in dt_range[::-1]:
#         reqId = app.request_historical_data(
#             reqId=1001,
#             contract=contract,
#             # TIMEZONE USED
#             endDateTime=dt.strftime("%Y%m%d %H:%M:%S")+ " America/Los_Angeles",
#             barSizeSetting="1 min",
#             durationStr="1 D",
#             whatToShow="AGGTRADES",
#             useRTH=1,
#             formatDate=1,
#             keepUpToDate=False
#         )

#         time.sleep(2)

#     app.disconnect()

#     df = app.data_to_dataframe()
#     df.to_csv("data/my_historical_data.csv", mode="w")