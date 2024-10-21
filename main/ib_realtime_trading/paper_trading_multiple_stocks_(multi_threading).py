#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

# Written by: Yutong Zhao
# on 2024-02-19

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys
# Append the path to the module to sys.path
module_path = r"C:\FinTech\mini_wt\time_diff\test_order_20240208_1.csv"
sys.path.insert(0, module_path)

# Now you can import the ibapi module
import ibapi
import threading
from copy import  deepcopy
import datetime
import pytz
from datetime import  datetime as dt
# The above could be sent to an independent module
import mini_wt.main.backtrader as bt
import pytz
import csv

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

        self.last_trade_time = None  # Time of the last trade
        self.is_in_position = False  # If we currently hold a position

        # Create SMA on 2nd data
        self.sma = bt.indicators.MovAv.SMA(self.data, period=self.p.smaperiod)

        print('--------------------------------------------------')
        print('Strategy Created')
        print('--------------------------------------------------')
        # Open a CSV file for writing
        self.csvfile = open(r'C:\wt\mini_wt\time_diff\test_multiple_order_20240220_1.csv', 'w', newline='')
        self.csvwriter = csv.writer(self.csvfile)

        # Write headers to the CSV file
        self.csvheaders = ['local_time', 'datetime', 'time_diff', 'open', 'high', 'low', 'close',
                           'volume', 'openinterest', 'ma', 'order_created_time', 'order_price']
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
        data = self.datas[0]
        print("data_ready: ", self.data_ready)
        print("datastatus: ", self.datastatus)
        eastern = pytz.timezone('US/Eastern')
        local_time = dt.now().astimezone(eastern)
        data_datetime = bt.num2date(self.data.datetime[0])

        # Ensure data_datetime is localized to Eastern Time
        if data_datetime.tzinfo is None or data_datetime.tzinfo.utcoffset(data_datetime) is None:
            data_datetime = eastern.localize(data_datetime.replace(tzinfo=None))
        else:
            data_datetime = data_datetime.astimezone(eastern)
        time_diff = (local_time - data_datetime).total_seconds()

        # Check for trade timing and execute accordingly
        current_time = dt.now().astimezone(pytz.timezone('US/Eastern'))
        if self.last_trade_time is None or (current_time - self.last_trade_time).total_seconds() >= 30:
            if not self.is_in_position:
                print("Order Type: Market")
                print("Order Size: 100")
                self.order = self.buy(size=100)
                self.is_in_position = True
            else:
                print("Order Type: Market")
                print("Order Size: 100")
                self.order = self.sell(size=100)
                self.is_in_position = False
            self.last_trade_time = current_time  # Update last trade time

        print(f"{self.data._name},\
                local_time: {local_time},\
                datetime: {data_datetime},\
                time_diff: {time_diff:.6f},\
                open: {self.data.open[0]},\
                high: {self.data.high[0]},\
                low: {self.data.low[0]},\
                close: {self.data.close[0]},\
                volume: {self.data.volume[0]},\
                openinterest: {self.data.openinterest[0]},\
                ma: {self.sma[0]},\
                order_created_time: {self.order_created_time},\
                order_price: {self.order_price}"
              )

        # CSV writing
        row = [local_time, data_datetime, time_diff, self.data.open[0], self.data.high[0], self.data.low[0],
               self.data.close[0], self.data.volume[0], self.data.openinterest[0], self.sma[0] if self.sma else 'nan',
               self.order_created_time, self.order_price]
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

def runstrategy(args):
    # args = parse_args()
    print(f"Running strategy for {args.data0}")
    # Create a cerebro
    cerebro = bt.Cerebro()
    # IBstore参数
    storekwargs = dict(
        host=args.host, port=args.port,
        clientId=args.clientId, timeoffset=not args.no_timeoffset,
        reconnect=args.reconnect, timeout=args.timeout,
        notifyall=args.notifyall, _debug=args.debug
    )

    if args.usestore:
        ibstore = bt.stores.IBStore(**storekwargs)

    if args.broker:
        broker = bt.brokers.IBBroker(**storekwargs)
        cerebro.setbroker(broker)

    timeframe = args.timeframe
    # Manage data1 parameters
    tf1 = args.timeframe1
    tf1 = tf1 if tf1 is not None else timeframe
    cp1 = args.compression1
    cp1 = cp1 if cp1 is not None else args.compression

    if args.resample or args.replay:
        datatf = datatf1 = bt.TimeFrame.Ticks
        datacomp = datacomp1 = 1
    else:
        datatf = timeframe
        datacomp = args.compression
        datatf1 = tf1
        datacomp1 = cp1

    fromdate = None
    if args.fromdate:
        dtformat = '%Y-%m-%d' + ('T%H:%M:%S' * ('T' in args.fromdate))
        fromdate = datetime.datetime.strptime(args.fromdate, dtformat)
    # 获取数据
    IBDataFactory = ibstore.getdata

    # 数据的参数
    datakwargs = dict(
        timeframe=datatf, compression=datacomp,
        historical=args.historical, fromdate=fromdate,
        rtbar=args.rtbar,
        qcheck=args.qcheck,
        what=args.what,
        backfill_start=not args.no_backfill_start,
        backfill=not args.no_backfill,
        latethrough=args.latethrough,
        tz=args.timezone
    )
    # Place the debug statement right after datakwargs is fully defined
    # print("Yutong Zhao Updating at RunStrategy--> Data fetching parameters:", datakwargs)

    # 如果没有用store模式并且没有用设置broker，更新参数
    if not args.usestore and not args.broker:  # neither store nor broker
        datakwargs.update(storekwargs)  # pass the store args over the data
    # 获取数据
   # datas = IBDataFactory(dataname=args.datas, **datakwargs)
    data0 = IBDataFactory(dataname=args.data0, **datakwargs)
    # 是否获取数据1
    data1 = None
    if args.data1 is not None:
        if args.data1 != args.data0:
            datakwargs['timeframe'] = datatf1
            datakwargs['compression'] = datacomp1
            data1 = IBDataFactory(dataname=args.data1, **datakwargs)
        else:
            data1 = data0

    rekwargs = dict(
        timeframe=tf1, compression=cp1,
        bar2edge=not args.no_bar2edge,
        adjbartime=not args.no_adjbartime,
        rightedge=not args.no_rightedge,
        takelate=not args.no_takelate,
    )

    if args.replay:
        cerebro.replaydata(data0, **rekwargs)

        if data1 is not None:
            rekwargs['timeframe'] = tf1
            rekwargs['compression'] = cp1
            cerebro.replaydata(data1, **rekwargs)

    elif args.resample:
        cerebro.resampledata(data0, **rekwargs)

        if data1 is not None:
            rekwargs['timeframe'] = tf1
            rekwargs['compression'] = cp1
            cerebro.resampledata(data1, **rekwargs)

    else:
        cerebro.adddata(data0)
        if data1 is not None:
            cerebro.adddata(data1)
    # 数据的有效期，这个地方需要额外考虑是0的时候，当天有效的设置，这里没有设置好，是0的时候，有效期基本上相当于市价单，没有成交就会立即撤单
    if args.valid is None:
        valid = None
    else:
        valid = datetime.timedelta(seconds=args.valid)
    # Add the strategy
    cerebro.addstrategy(TestStrategy,
                        smaperiod=args.smaperiod,
                        trade=args.trade,
                        exectype=args.exectype,
                        stake=args.stake,
                        stopafter=args.stopafter,
                        valid=valid,
                        cancel=args.cancel,
                        donotsell=args.donotsell,
                        stoptrail=args.stoptrail,
                        stoptraillimit=args.traillimit,
                        trailamount=args.trailamount,
                        trailpercent=args.trailpercent,
                        limitoffset=args.limitoffset,
                        oca=args.oca,
                        bracket=args.bracket)

    # Live data ... avoid long data accumulation by switching to "exactbars"
    cerebro.run(exactbars=args.exactbars)

    if args.plot and args.exactbars < 1:  # plot if possible
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

def trade_stocks(stock):
    temp_args = deepcopy(args)
    temp_args['data0'] = stock
    new_args = AO(temp_args)
    runstrategy(new_args)


if __name__ == '__main__':
    stocks = ['EUR.USD-CASH-IDEALPRO']
    threads = []

    for stock in stocks:
        t = threading.Thread(target=trade_stocks, args=(stock,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()