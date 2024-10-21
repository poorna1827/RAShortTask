###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt
import datetime

import backtrader_ib_insync as ibnew

class TestPrinter(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.datetime(0)
        print(f'{dt}, {txt}')

    def __init__(self):
        self.open = self.datas[0].open
        self.high = self.datas[0].high
        self.low = self.datas[0].low
        self.close = self.datas[0].close
        self.volume = self.datas[0].volume
        self.openinterest = self.datas[0].openinterest

    def next(self):
        self.log(f'Open:{self.open[0]:.2f}, \
                   High:{self.high[0]:.2f}, \
                   Low:{self.low[0]:.2f}, \
                   Close:{self.close[0]:.2f}, \
                   Volume:{self.volume[0]:.2f}, \
                   OpenInterest:{self.volume[0]:.2f}' )

cerebro = bt.Cerebro()

start = datetime.datetime(2023, 1, 1)
end = datetime.datetime(2023, 2, 6)

storekwargs = dict(
        host='127.0.0.1', port=7497,
        clientId=None, timeoffset=False,
        reconnect=3, timeout=3,
        notifyall=False, _debug=False)

ibstore = ibnew.IBStore(**storekwargs)

print("Using New IBstore")

datakwargs = dict(
        timeframe=bt.TimeFrame.Ticks,
        what='BID_ASK',
        rtbar=False,
        latethrough=True,
        tz=None
    )

data0 = ibstore.getdata(dataname='GOOG-STK-SMART-USD', **datakwargs)

print("Data added to cerebro")
# cerebro.resampledata(data0, timeframe=bt.TimeFrame.Seconds, compression=10)
cerebro.adddata(data0)

# Add the printer as a strategy
cerebro.addstrategy(TestPrinter)

cerebro.run()