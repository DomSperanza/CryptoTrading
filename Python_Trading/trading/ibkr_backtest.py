import backtrader as bt

from atreyu_backtrader_api import IDBData
from strategies import TestStrategy

import datetime as dt
from datetime import datetime, date, time

cerebro = bt.Cerebro()

data = IBData(host='127.0.0.1', port=7497, clientId=35,
                name="AAPL",
                dataname="AAPL",
                secType='STK',
                exchange='SMART',
                currency='USD',
                historical=True
                )

cerebro.adddata(data)

#set desired cash start
cerebro.broker.setcash(10000.0)

#add the test strat
cerebro.addstrategy(TestStrategy)

#add a FixedSize sizer according to the stake
cerebro.addsizer(bt.sizers.FixedSize, stake=10)

cerebro.run()

# print final result
print(f'Final Portfolio Value: {cerebro.broker.getvalue():.2f}')