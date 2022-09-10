import backtrader as bt

from atreyu_backtrader_api import IDBData
from atreyu_backtrader_api import IBStore

from strategies import TestStrategy

import datetime as dt
from datetime import datetime, date, time

cerebro = bt.Cerebro()

ibstore = IBStore(host='127.0.0.1',
port=7497,
clientId=35)

data = ibstore.getdata(name="AAPL",
                dataname="AAPL",
                secType='STK',
                exchange='SMART',
                currency='USD'
                )

cerebro.adddata(data)

broker = ibstore.getbroker()

#set the broker
cerebro.setbroker(broker)

#add the test strat
cerebro.addstrategy(TestStrategy)

#add a FixedSize sizer according to the stake
cerebro.addsizer(bt.sizers.FixedSize, stake=10)

cerebro.run()