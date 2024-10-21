#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime as dt
from datetime import timedelta
import pytz

import numpy as np
import pandas as pd
from math import isclose
import mini_wt.main.backtrader as bt
from mini_wt.main.backtrader.utils import flushfile  # win32 quick stdout flushing

class CVX_Markowitz_Strategy(bt.Strategy):
    params = (
        ('quantile_risk', 0.8),
        ('quantile_turn', 0.8),
        ('quantile_lev', 1),
        ('training', False),
    )

    def __init__(self):
        print("Initializing Strategy")
        self.data_ready = False

        # To control operation entries
        self.orderid = list()
        self.order = None
        self.order_created_time = None
        self.executed_time = None
        self.execution_time_diff = None
        self.executed_price = None
        self.executed_value = None
        self.executed_comm = None
        self.counttostop = 0
        self.datastatus = 0

        # 保存现有持仓的股票
        self.position_dict = {}
        # 当前有交易的股票
        self.stock_dict = {}

        self.tickers = selected_stocks

        self.w_prev = np.zeros(len(self.datas))
        # self.tickers = np.array([dat.p.name for dat in self.datas])
        print('loading lru cache data')

        print('--------------------------------------------------')
        print('Strategy Created')
        print('--------------------------------------------------')

    def notify_data(self, data, status, *args, **kwargs):
        print('*' * 5, 'DATA NOTIF:', data._getstatusname(status), *args)
        # Additional print to check data status
        print("Yutong Zhao Updating --> Data status change:", status, "Args:", args, "Kwargs:", kwargs)
        if status == data.LIVE:
            # self.counttostop = self.p.stopafter
            self.datastatus = 1  # 如果是实盘数据开始了，那么，datastatus就变为1

    def notify_store(self, msg, *args, **kwargs):
        # 显示从IB传送过来的信息
        print('*' * 5, 'STORE NOTIF:', msg)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enougth cash
        if order.status in [order.Canceled, order.Margin]:
            if order.isbuy():
                print("BUY FAILED, Cancelled or Margin")
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            if order.isbuy():
                print(
                    "BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                print(
                    "SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )

            self.bar_executed = len(self)

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        print("OPERATION PROFIT, GROSS %.2f, NET %.2f" % (trade.pnl, trade.pnlcomm))

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

    def prenext(self):
        print("成功进入prenext")

        self.next(frompre=True)

    def next(self, frompre=False):
        current_date = self.datas[0].datetime.date(0).strftime("%Y-%m-%d")

        self.curr_datetime = pd.to_datetime(self.datas[0].datetime.date(0))
        self.interest = 0.0003

        quantities = np.zeros(len(self.datas))
        eastern = pytz.timezone('US/Eastern')
        current_time = dt.datetime.now().astimezone(eastern)

        for data in self.datas:
            print("data_ready: ", self.data_ready)
            print("datastatus: ", self.datastatus)

            if self.datastatus > 0:
                local_time = dt.datetime.now().astimezone(eastern)
                raw_datetime = data.datetime[0]

                # Check if the raw_datetime is a Backtrader float format
                data_datetime = bt.num2date(raw_datetime)

                # Ensure data_datetime is correctly localized
                if data_datetime.tzinfo is None or data_datetime.tzinfo.utcoffset(data_datetime) is None:
                    data_datetime = eastern.localize(data_datetime.replace(tzinfo=None))
                else:
                    data_datetime = data_datetime.astimezone(eastern)

                time_diff = (local_time - data_datetime).total_seconds()
                print(
                    f"{data._name}, local_time: {local_time}, datetime: {data_datetime}, time_diff: {time_diff:.6f}, open: {data.open[0]}, high: {data.high[0]}, low: {data.low[0]}, close: {data.close[0]}, volume: {data.volume[0]}, openinterest: {data.openinterest[0]}, order_created: {self.order_created_time}, executed_time: {self.executed_time}, execution_time_diff: {self.execution_time_diff}, executed_price: {self.executed_price}, executed_value: {self.executed_value}, executed_comm: {self.executed_comm}")

                # Reset order execution details after writing to CSV
                self.executed_time = None
                self.execution_time_diff = None
                self.executed_price = None
                self.executed_value = None
                self.executed_comm = None

            if current_time.strftime("%H:%M") == "10:21":
                for idx, data in enumerate(self.datas):
                    data_date = data.datetime.date(0).strftime("%Y-%m-%d")
                    if current_date == data_date:
                        quantities[idx] = self.positionsbyname[data._name].size

                self.quantities_prev = quantities


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
    fromdate = dt.datetime.strptime(ao.fromdate, '%Y-%m-%d') if ao.fromdate else None
    #fromdate = None
    #if args.fromdate:
     #   dtformat = '%Y-%m-%d' + ('T%H:%M:%S' * ('T' in args.fromdate))
      #  fromdate = datetime.datetime.strptime(args.fromdate, dtformat)

    # 获取数据
    IBDataFactory = ibstore.getdata

    datakwargs = {
        'timeframe': timeframe, 'compression': compression,
        'historical': ao.historical, 'fromdate': fromdate,
        'rtbar': ao.rtbar, 'qcheck': ao.qcheck,
        'what': ao.what, 'backfill_start': not ao.no_backfill_start,
        'backfill': not ao.no_backfill, 'latethrough': ao.latethrough,
        'tz': ao.timezone
    }

    # Place the debug statement right after datakwargs is fully defined
    print("Yutong Zhao Updating at RunStrategy--> Data fetching parameters:", datakwargs)

    rekwargs = dict(
        timeframe=timeframe, compression=compression
    )

    for stock_symbol in tickers:
        if ibstore:
            datakwargs['dataname'] = stock_symbol
            data_feed = ibstore.getdata(**datakwargs)
            cerebro.resampledata(data_feed, **rekwargs)

    # 数据的有效期，这个地方需要额外考虑是0的时候，当天有效的设置，这里没有设置好，是0的时候，有效期基本上相当于市价单，没有成交就会立即撤单
    # Add the strategy
    cerebro.addstrategy(CVX_Markowitz_Strategy)  # Add strategy parameters if needed

    # Run the strategy
    cerebro.run()

    if ao.plot:
        cerebro.plot()


args = {"exactbars": 0,  # exactbars level, use 0/-1/-2 to enable plotting
        "stopafter": 0,  # Stop after x lines of LIVE data，默认情况下，永远不停止，如果是一个大于0的整数，就代表多少个next之后会停止
        "plot": True,  # Plot if possible
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
        "rtbar": False,  # 是否使用5秒钟的bar代替250ms的tick，默认是不会
        "historical": False,  # 是否仅仅下载历史数据，默认是否
        "fromdate": False,  # 从哪里开始下载历史数据，参数可以设置具体的时间YYYY-MM-DD[THH:MM:SS]
        "replay": False,  # replay
        "resample": True,  # resample,和replay两个功能不能同时都设置成True
        "timeframe": bt.TimeFrame.Minutes,  # 交易的时间间隔
        "compression": 2,  # 多少个交易的时间间隔形成一个bar
        "timeframe1": bt.TimeFrame.Seconds,  # data1的
        "compression1": 5,  # data1的
        "no_takelate": False,  # 当latethrough设置成True的时候，resample或者replay形成新的bar的时候，是否使用来的比较迟的tick
        "no_bar2edge": False,  # no bar2edge for resample/replay
        "no_adjbartime": False,  # no adjbartime for resample/replay
        "no_rightedge": False,  # no rightedge for resample/replay
        "broker": True,  # 使用IB作为broker
        "trade": False,  # 是否进行买卖活动，设置成False的时候，不会进行买卖
        "donotsell": False,  # 买了之后是否卖，默认是买了之后会卖的
        "exectype": bt.Order.Market,  # 下单的类型，默认是市价单
        "stake": 1,  # 每次下单的手数
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

    selected_stocks = pd.read_csv(r"C:\FinTech\wt_data\selected_sp_100_ticker_list.txt",
                names=['tickers'], header=None)['tickers'].to_list()[0:1]

    tickers = [ticker+"-STK-SMART-USD" for ticker in selected_stocks]


    ao = AO(args)

    runstrategy(ao, tickers)