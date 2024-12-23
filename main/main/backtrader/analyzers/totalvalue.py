from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from collections import OrderedDict
from mini_wt.main.backtrader import Analyzer


class TotalValue(Analyzer):
    '''This analyzer will get total value from every next.
    Params:
    Methods:
      - get_analysis
        Returns a dictionary with returns as values and the datetime points for
        each return as keys
    '''

    params = ( )

    def start(self):
        super(TotalValue, self).start()
        self.vals = OrderedDict()
        self.cash = OrderedDict()

    def next(self):
        # Calculate the return
        super(TotalValue, self).next()
        # print("total_value",self.datas[0].datetime.date(0),self.strategy.broker.getvalue())
        self.vals[self.datas[0].datetime.datetime(0)] = self.strategy.broker.getvalue()
        self.cash[self.datas[0].datetime.datetime(0)] = self.strategy.broker.getcash()

    def get_analysis(self):
        return (self.vals, self.cash)