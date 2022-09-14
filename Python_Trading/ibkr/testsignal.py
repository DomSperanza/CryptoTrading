import backtrader as bt

class MySignal(bt.Indicator):
    lines = ('signal',)
    params = (('period', 30),)

    def __init__(self) -> None:
        self.lines.signal = self.data - bt.indicators.SMA(period=self.p.period)