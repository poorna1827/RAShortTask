# Written by: Yutong Zhao
# 2023-12-30

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import mini_wt.main.backtrader as bt

if __name__ == '__main__':
    cerebro = bt.Cerebro()

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())