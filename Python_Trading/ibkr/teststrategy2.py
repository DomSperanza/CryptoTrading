from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


import backtrader as bt
import backtrader.indicators as btind


class SMA_CrossOver(bt.Strategy):

    params = (
        ('fast', 10), 
        ('slow', 30),
        ('printlog', False),)

    def __init__(self):

        sma_fast = btind.SMA(period=self.p.fast)
        sma_slow = btind.SMA(period=self.p.slow)

        self.buysig = btind.CrossOver(sma_fast, sma_slow)

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function for this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt}, {txt}')

    def next(self):
        if self.position.size:
            if self.buysig < 0:
                self.sell()

        elif self.buysig > 0:
            self.buy()

    def stop(self):
        self.log(
            f'''(Fast {self.params.fast})
             (Slow {self.params.slow})
             Ending Value {self.broker.getvalue():.2f}''',
            doprint=True)