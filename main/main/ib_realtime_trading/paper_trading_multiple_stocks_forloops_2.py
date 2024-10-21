# Yutong Zhao
# 2024-02-21

#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys
# Append the path to the module to sys.path
module_path = r"C:\FinTech\source\pythonclient"
sys.path.insert(0, module_path)

# Now you can import the ibapi module
import ibapi
import datetime
import pytz
from datetime import  datetime as dt
# The above could be sent to an independent module
import mini_wt.main.backtrader as bt
import pytz
import csv
import time
from mini_wt.main.backtrader.utils import flushfile  # win32 quick stdout flushing


class TestStrategy(bt.Strategy):
    # 策略的参数，具体的参数的意义在下面有注释
    params = dict(
        smaperiod=5,
        trade=True,
        stake=10,
        exectype=bt.Order.Market,
        stopafter=0,
        valid=None,
        cancel=0,
        donotsell=False,
        stoptrail=False,
        stoptraillimit=False,
        trailamount=None,
        trailpercent=None,
        limitoffset=None,
        oca=False,
        bracket=False,
    )

    def __init__(self):
        # For testing config args
        print("initializing strategy")
        self.data_ready = False
        # self.highest = bt.ind.Highest(self.data.high, period=200)
        # self.lowest = bt.ind.Lowest(self.data.low, period=200)

        # To control operation entries
        self.orderid = list()
        self.order = None
        self.order_created_time = None
        self.order_price = None

        self.executed_time = None
        self.execution_time_diff = None
        self.executed_price = None
        self.executed_value = None
        self.executed_comm = None
        self.counttostop = 0
        self.datastatus = 0

        # self.last_trade_time = None  # Time of the last trade
        # self.is_in_position = False  # If we currently hold a position

        self.last_trade_time = {}
        self.is_in_position = {}
        for i, d in enumerate(self.datas):
            name = d._name
            self.last_trade_time[name] = None
            self.is_in_position[name] = False

        # Create SMA on 2nd data
        self.sma = bt.indicators.MovAv.SMA(self.data, period=self.p.smaperiod)

        print('--------------------------------------------------')
        print('Strategy Created')
        print('--------------------------------------------------')
        # Open a CSV file for writing
        self.csvfile = open(r'C:\wt\mini_wt\time_diff\test_multi_order_20240221_8_(ticker50).csv', 'w', newline='')
        self.csvwriter = csv.writer(self.csvfile)

        # Write headers to the CSV file
        self.csvheaders = ['symbol', 'local_time', 'datetime', 'time_diff', 'open_price', 'high_price', 'low_price', 'close_price',
                           'volume', 'open_interest', 'ma']
        self.csvwriter.writerow(self.csvheaders)
        self.order_creation_time = None
        self.order_price = None

    def notify_data(self, data, status, *args, **kwargs):
        # print('*' * 5, 'DATA NOTIF:', data._getstatusname(status), *args)
        print('Data Status =>', data._getstatusname(status))
        # Additional print to check data status
        print("Yutong Zhao Updating at notify_data --> Data status change (status printed here):", status, "Args:", args, "Kwargs:", kwargs)
        if status == data.LIVE:
            self.data_ready = True
            self.counttostop = self.p.stopafter
            self.datastatus = 1  # 如果是实盘数据开始了，那么，datastatus就变为1

    def notify_store(self, msg, *args, **kwargs):
        # 显示从IB传送过来的信息
        print('*' * 5, 'STORE NOTIF:', msg)

    def notify_order(self, order):
        print('Order Status:', order.getstatusname())

        if order.status in [order.Submitted]:
            # Capture the order creation time for submitted orders
            print('Order was submitted.')
            self.order_created_time = dt.now().astimezone(pytz.timezone('US/Eastern'))
            # Do not attempt to print the executed price here
            print('Order Submitted at:', self.order_created_time)
            return

        if order.status in [order.Accepted]:
            # Indicate that the order was accepted
            print('Order was accepted.')
            # Since the order is just accepted, execution details like price are not available yet
            return

        if order.status in [order.Completed, order.PartiallyCompleted]:
            # Now the order is completed or partially completed, we can access execution details
            print('Order is completed or PartiallyCompleted.')
            if order.isbuy():
                print("BUY EXECUTED, Price:", order.executed.price)
            elif order.issell():
                print("SELL EXECUTED, Price:", order.executed.price)

            # Reset order creation time
            self.order_created_time = None

            # Example of additional handling for completed orders
            # Here you can safely access execution details like executed price
            print(
                "EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                % (order.executed.price, order.executed.value, order.executed.comm)
            )

            # Update any internal state as needed
            self.order = None  # Indicate there's no pending order

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        print("OPERATION PROFIT, GROSS %.2f, NET %.2f" % (trade.pnl, trade.pnlcomm))

    def prenext(self):
        print("成功进入prenext")

        self.next(frompre=True)

    def next(self, frompre=False):
        for data in self.datas:
            data_name = data._name
            eastern = pytz.timezone('US/Eastern')
            local_time = dt.now().astimezone(eastern)
            data_datetime = bt.num2date(self.data.datetime[0])

            # Ensure data_datetime is localized to Eastern Time
            if data_datetime.tzinfo is None or data_datetime.tzinfo.utcoffset(data_datetime) is None:
                data_datetime = eastern.localize(data_datetime.replace(tzinfo=None))
            else:
                data_datetime = data_datetime.astimezone(eastern)
            time_diff = (local_time - data_datetime).total_seconds()

            current_time = dt.now().astimezone(pytz.timezone('US/Eastern'))
            # Update to use dictionary for each data feed
            if self.last_trade_time[data_name] is None or (
                    current_time - self.last_trade_time[data_name]).total_seconds() >= 30:
                if not self.is_in_position[data_name]:
                    self.order = self.buy(data=data, size=2)
                    self.is_in_position[data_name] = True
                else:
                    self.order = self.sell(data=data, size=2)
                    self.is_in_position[data_name] = False
                self.last_trade_time[data_name] = current_time  # Update last trade time for the specific data feed

            # Console Printing for each data
            print(f"{data_name}, local_time: {local_time}, datetime: {data_datetime}, time_diff: {time_diff:.6f},"
                  f" open: {data.open[0]}, high: {data.high[0]}, low: {data.low[0]},"
                  f" close: {data.close[0]}, volume: {data.volume[0]}, openinterest: {data.openinterest[0]},"
                  f" ma: {self.sma[0] if hasattr(self, 'sma') and self.sma else 'nan'}")

            # CSV Writing for each data
            row = [data_name, local_time, data_datetime, time_diff, data.open[0], data.high[0], data.low[0],
                   data.close[0], data.volume[0], data.openinterest[0],
                   self.sma[0] if hasattr(self, 'sma') and self.sma else 'nan']
            self.csvwriter.writerow(row)
            self.csvfile.flush()

            if self.datastatus:
                self.datastatus += 1

    def start(self):
        print("开始运行，获取时区")
        if self.data0.contractdetails is not None:
            print('Timezone from ContractDetails: {}'.format(
                self.data0.contractdetails.timeZoneId))

        header = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume',
                  'OpenInterest', 'SMA']
        print(', '.join(header))
        print(dir(self.data0.contractdetails))

        self.done = False

def runstrategy(ao, args):
    # Create a cerebro
    cerebro = bt.Cerebro()
    # Use the AO object for configuration
    storekwargs = {
        'host': ao.host, 'port': ao.port,
        'clientId': ao.clientId, 'timeoffset': not ao.no_timeoffset,
        'reconnect': ao.reconnect, 'timeout': ao.timeout,
        'notifyall': ao.notifyall, '_debug': ao.debug
    }

    ibstore = None
    if ao.usestore:
        ibstore = bt.stores.IBStore(**storekwargs)

    if ao.broker and ibstore:
        broker = bt.brokers.IBBroker(**storekwargs)
        cerebro.setbroker(broker)

    timeframe = ao.timeframe
    compression = ao.compression
    fromdate = datetime.datetime.strptime(ao.fromdate, '%Y-%m-%d') if ao.fromdate else None

    datakwargs = {
        'timeframe': timeframe, 'compression': compression,
        'historical': ao.historical, 'fromdate': fromdate,
        'rtbar': ao.rtbar, 'qcheck': ao.qcheck,
        'what': ao.what, 'backfill_start': not ao.no_backfill_start,
        'backfill': not ao.no_backfill, 'latethrough': ao.latethrough,
        'tz': ao.timezone
    }

    for stock_symbol in stocks:
        if ibstore:
            datakwargs['dataname'] = stock_symbol
            data_feed = ibstore.getdata(**datakwargs)
            cerebro.adddata(data_feed, name=stock_symbol)

    # Add the strategy
    cerebro.addstrategy(TestStrategy)  # Add strategy parameters if needed

    # Run the strategy
    cerebro.run()

    if ao.plot:
        cerebro.plot()



args = {"exactbars": 1,  # exactbars level, use 0/-1/-2 to enable plotting
        "stopafter": 0,  # Stop after x lines of LIVE data，默认情况下，永远不停止，如果是一个大于0的整数，就代表多少个next之后会停止
        "plot": False,  # Plot if possible
        "usestore": True,  # 使用ib的时候是否使用store模式
        "notifyall": False,  # 是否把所有信息都会通过store notify告知给策略
        "debug": False,  # 默认不显示所有的从IB获取的信息
        "host": '127.0.0.1',  # 连接TWS的时候使用的host
        "port": 7497,  # 连接TWS的端口号，默认是7496,模拟交易使用7497
        "qcheck": 0.5,  # 在resample或者replay的时候多少时间间隔检查一次，用于生成bar
        "clientId": 95,  # 默认情况下可以随机生成一个，开多个TWS的时候可以指定每个clientid，有一个master id 可以控制其他的clientid
        "no_timeoffset": False,  # 是否使用IB的系统时间和本地时钟之间做时间的补偿，使得本地时间和系统时间能够对齐，以方便能够生成bar更准确
        "reconnect": 3,  # 当连接中断之后，尝试的重新连接次数
        "timeout": 3,  # 每次尝试连接的时候，间隔的时间，默认是3秒
        "data0": True,  # 加载到系统的第一个数据
        "data1": None,  # 加载到系统的第二个数据
        "timezone": "US/Eastern",  # 默认情况下，根据从IB获取的时间设置时区，也可以自己去设置
        "what": None,  # 用于请求的历史数据类型
        "no_backfill_start": True,  # 默认开始的时候不填充历史数据
        "latethrough": True,  # 当resample或者replay的时候，让来的太迟的tick传递过去
        "no_backfill": True,  # 当连接中断之后，是否填充，默认是不填充
        "rtbar": True,  # 是否使用5秒钟的bar代替250ms的tick，默认是不会
        "historical": False,  # 是否仅仅下载历史数据，默认是否
        "fromdate": False,  # 从哪里开始下载历史数据，参数可以设置具体的时间YYYY-MM-DD[THH:MM:SS]
        "smaperiod": 5,  # 策略运行使用的参数
        "replay": False,  # replay
        "resample": True,  # resample,和replay两个功能不能同时都设置成True
        "timeframe": bt.TimeFrame.Seconds,  # 交易的时间间隔
        "compression": 10,  # 多少个交易的时间间隔形成一个bar
        "timeframe1": bt.TimeFrame.Seconds,  # data1的
        "compression1": 10,  # data1的
        "no_takelate": False,  # 当latethrough设置成True的时候，resample或者replay形成新的bar的时候，是否使用来的比较迟的tick
        "no_bar2edge": False,  # no bar2edge for resample/replay
        "no_adjbartime": False,  # no adjbartime for resample/replay
        "no_rightedge": False,  # no rightedge for resample/replay
        "broker": True,  # 使用IB作为broker
        "trade": True,  # 是否进行买卖活动，设置成False的时候，不会进行买卖
        "donotsell": False,  # 买了之后是否卖，默认是买了之后会卖的
        "exectype": bt.Order.Market,  # 下单的类型，默认是市价单
        "stake": 100,  # 每次下单的手数
        "valid": None,  # 订单的有效期设置，None代表一直有效，0代表当天有效
        # 下面几种止损不能共存，只能选一个
        "stoptrail": False,  # 是否下一个市价止损单，默认是否
        "traillimit": False,  # 是否下一个限价跟踪止损单，默认是否
        "oca": False,  # 是否下一个oca订单，应该是backtrader中的oco订单
        "bracket": False,  # 是否下一个一篮子订单
        # 下面几种也是不能共存的
        "trailamount": None,  # StopTrail订单设置的参数
        "trailpercent": None,  # StopTrail订单设置的参数
        "limitoffset": None,  # 订单的参数
        "cancel": 0,  # 限价单使用，如果n个bar之后还没有成交，取消订单
        }


class AO():
    def __init__(self, args):
        for key, value in args.items():
            setattr(self, key, value)


if __name__ == '__main__':
    stocks = ['BAC-STK-SMART-USD',    'WMT-STK-SMART-USD',    'PBR-STK-SMART-USD',    'WFC-STK-SMART-USD',    'PFE-STK-SMART-USD',    'MSFT-STK-SMART-USD',    'UPS-STK-SMART-USD',    'UNH-STK-SMART-USD',    'TTE-STK-SMART-USD',    'MRK-STK-SMART-USD',    'AAPL-STK-SMART-USD',    'VALE-STK-SMART-USD',    'VZ-STK-SMART-USD',    'C-STK-SMART-USD',    'GOOGL-STK-SMART-USD',    'JPM-STK-SMART-USD',    'HD-STK-SMART-USD',    'HSBC-STK-SMART-USD',    'TM-STK-SMART-USD',    'TSM-STK-SMART-USD',    'CMCSA-STK-SMART-USD',    'JNJ-STK-SMART-USD',    'XOM-STK-SMART-USD',    'MS-STK-SMART-USD',    'RIO-STK-SMART-USD',    'T-STK-SMART-USD',    'BHP-STK-SMART-USD',    'CVX-STK-SMART-USD',    'GS-STK-SMART-USD',    'SONY-STK-SMART-USD',    'PG-STK-SMART-USD',    'RY-STK-SMART-USD',    'NVS-STK-SMART-USD',    'INTC-STK-SMART-USD',    'TD-STK-SMART-USD',    'VNQ-STK-SMART-USD',    'EWJ-STK-SMART-USD',    'XLB-STK-SMART-USD',    'XLI-STK-SMART-USD',    'XLF-STK-SMART-USD',    'XLE-STK-SMART-USD',    'SOXX-STK-SMART-USD',    'IVW-STK-SMART-USD',    'IJR-STK-SMART-USD',    'SPY-STK-SMART-USD',    'IWB-STK-SMART-USD',    'IVE-STK-SMART-USD',    'IWO-STK-SMART-USD',    'IVV-STK-SMART-USD',    'QQQ-STK-SMART-USD',    'IWM-STK-SMART-USD',    'IJH-STK-SMART-USD',    'DIA-STK-SMART-USD',    'MDY-STK-SMART-USD',    'IWV-STK-SMART-USD']

    ao = AO(args)
    runstrategy(ao, stocks)