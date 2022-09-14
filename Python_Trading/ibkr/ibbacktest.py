import backtrader as bt

# !requires 3.2.2
# https://stackoverflow.com/questions/63471764/importerror-cannot-import-name-warnings-from-matplotlib-dates
import matplotlib
from teststrategy import TestStrategy
from teststrategy2 import SMA_CrossOver
from testsignal import MySignal
from ibdataapp import IBDataApp
from ibcontract import IBContract
import pandas as pd

import datetime as dt
from datetime import datetime, date, time

cerebro = bt.Cerebro()


# data = IBDataApp(host='127.0.0.1', port=7497, clientId=0)
# contract = IBContract("BTC")

datapath = "data\my_historical_data.csv"

df = pd.read_csv(datapath)
df['date'] = pd.to_datetime(df['date'])
df.set_index('date',inplace=True)
# print(df.head())

data = bt.feeds.PandasData(dataname=df, openinterest=None)
cerebro.adddata(data)

# # Set our desired cash start
cerebro.broker.setcash(100000.0)
# cerebro.addsizer(bt.sizers.FixedSize, stake=10)
cerebro.broker.setcommission(commission=0.001)

# # Add the test strategy
# cerebro.addstrategy(TestStrategy)

cerebro.optstrategy(
    SMA_CrossOver,
    fast=range(5,15),
    slow=range(30,40),
)

# Add a signal (instead of strategy)
# cerebro.add_signal(bt.SIGNAL_LONGSHORT, MySignal)

print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

cerebro.run(maxcpus=1)

print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

# cerebro.plot(style='bar')