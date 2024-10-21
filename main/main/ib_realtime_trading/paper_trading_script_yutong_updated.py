#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import datetime
import pytz

# The above could be sent to an independent module
import mini_wt.main.backtrader as bt
from mini_wt.main.backtrader.utils import flushfile  # win32 quick stdout flushing


class TestStrategy(bt.Strategy):
    # 策略的参数，具体的参数的意义在下面有注释
    params = dict(
        smaperiod=5,
        trade=False,
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
        # To control operation entries
        self.orderid = list()
        self.order = None

        self.counttostop = 0
        self.datastatus = 0

        # Create SMA on 2nd data
        self.sma = bt.indicators.MovAv.SMA(self.data, period=self.p.smaperiod)

        print('--------------------------------------------------')
        print('Strategy Created')
        print('--------------------------------------------------')

    def notify_data(self, data, status, *args, **kwargs):
        print('*' * 5, 'DATA NOTIF:', data._getstatusname(status), *args)
        # Additional print to check data status
        print("Yutong Zhao Updating --> Data status change:", status, "Args:", args, "Kwargs:", kwargs)
        if status == data.LIVE:
            self.counttostop = self.p.stopafter
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

    def prenext(self):
        print("成功进入prenext")

        self.next(frompre=True)

    def next(self, frompre=False):

        data = self.datas[0]
        print(f"Yutong Zhao Updating --> Data check at next start: Open: {data.open[0]}, High: {data.high[0]}, Low: {data.low[0]}, Close: {data.close[0]}, Volume: {data.volume[0]}, OpenInterest: {data.openinterest[0]}")
        # 指标值
        # 布林带上轨
        if data.close[0] != data.close[0]:  # Checking for nan
            print("Warning: Close price is nan")
        sma = self.sma

        # print("成功进入next")
        # 准备显示第一个数据
        # txt = list()
        # txt.append('Data0')
        # txt.append('%04d' % len(self.data0))
        # dtfmt = '%Y-%m-%dT%H:%M:%S.%f'
        # txt.append('{}'.format(self.data.datetime[0]))
        # txt.append('%s' % self.data.datetime.datetime(0).strftime(dtfmt))
        # txt.append('{}'.format(self.data.open[0]))
        # txt.append('{}'.format(self.data.high[0]))
        # txt.append('{}'.format(self.data.low[0]))
        # txt.append('{}'.format(self.data.close[0]))
        # txt.append('{}'.format(self.data.volume[0]))
        # txt.append('{}'.format(self.data.openinterest[0]))
        # txt.append('{}'.format(self.ma[0]))
        if self.datastatus > 0:
            print(f"{self.data._name},\
                datetime:{bt.num2date(self.data.datetime[0])} , \
                open:{self.data.open[0]},\
                high:{self.data.high[0]},\
                low:{self.data.low[0]},\
                close:{self.data.close[0]},\
                volume:{self.data.volume[0]},\
                openinterest:{self.data.openinterest[0]},\
                ma:{self.sma[0]}")
        # 如果有第二个数据，那么也打印第二个数据
        if len(self.datas) > 1 and len(self.data1):
            # txt = list()
            # txt.append('Data1')
            # txt.append('%04d' % len(self.data1))
            # dtfmt = '%Y-%m-%dT%H:%M:%S.%f'
            # txt.append('{}'.format(self.data1.datetime[0]))
            # txt.append('%s' % self.data1.datetime.datetime(0).strftime(dtfmt))
            # txt.append('{}'.format(self.data1.open[0]))
            # txt.append('{}'.format(self.data1.high[0]))
            # txt.append('{}'.format(self.data1.low[0]))
            # txt.append('{}'.format(self.data1.close[0]))
            # txt.append('{}'.format(self.data1.volume[0]))
            # txt.append('{}'.format(self.data1.openinterest[0]))
            # txt.append('{}'.format(float('NaN')))
            # print(', '.join(txt))
            print(f"{self.data1._name},\
                datetime:{bt.num2date(self.data1.datetime[0])} , \
                open:{self.data1.open[0]},\
                high:{self.data1.high[0]},\
                low:{self.data1.low[0]},\
                close:{self.data1.close[0]},\
                volume:{self.data1.volume[0]},\
                openinterest:{self.data1.openinterest[0]},\
                ma:{self.sma[0]}")
        # 多少个next之后策略停止
        if self.counttostop:  # stop after x live lines
            self.counttostop -= 1
            if not self.counttostop:
                self.env.runstop()
                return
        # 如果trade设置的是False，下面将不会运行
        if not self.p.trade:
            return
        self.position_size = self.getposition(self.data).size
        print(f"self.datastatus:{self.datastatus},position_size:{self.position_size},len(self.orderid):{len(self.orderid)}")
        # 如果是实盘数据，并且没有持仓，并且没有下单
        if self.datastatus and self.position_size == 0 and len(self.orderid) < 1 and data.close[0] > sma[0] and data.close[-1] < sma[-1]:
            print("准备下单")
            # 如果不是oca订单类型，就直接下一个市价单，否则按照当前价格的90%下一个限价单，有效期是默认取消前有效，如果设置的是0的话，当天有效
            exectype = self.p.exectype if not self.p.oca else bt.Order.Limit
            close = self.data0.close[0]
            price = round(close * 1.001, 2)
            self.order = self.buy(size=self.p.stake,
                                  exectype=exectype,
                                  price=price,
                                  valid=self.p.valid,
                                  transmit=not self.p.bracket)

            self.orderid.append(self.order)
            print(f"下单成功:exectype-{exectype},self.p.bracket:{self.p.bracket},self.p.oca:{self.p.oca}")
            # 如果是一篮子订单，按照90%的价格设置止损价，按照110%的价格设置止盈价
            if self.p.bracket:
                # low side
                self.sell(size=self.p.stake,
                          exectype=bt.Order.Stop,
                          price=round(price * 0.90, 2),
                          valid=self.p.valid,
                          transmit=False,
                          parent=self.order)

                # high side
                self.sell(size=self.p.stake,
                          exectype=bt.Order.Limit,
                          price=round(close * 1.10, 2),
                          valid=self.p.valid,
                          transmit=True,
                          parent=self.order)
            # 如果是oca订单，按照80%的价格下一个限价单
            elif self.p.oca:
                self.buy(size=self.p.stake,
                         exectype=bt.Order.Limit,
                         price=round(self.data0.close[0] * 0.80, 2),
                         oco=self.order)
            # 如果是跟踪止损单
            elif self.p.stoptrail:
                self.sell(size=self.p.stake,
                          exectype=bt.Order.StopTrail,
                          # price=round(self.data0.close[0] * 0.90, 2),
                          valid=self.p.valid,
                          trailamount=self.p.trailamount,
                          trailpercent=self.p.trailpercent)
            # 如果是跟踪止损限价单
            elif self.p.stoptraillimit:
                p = round(self.data0.close[0] - self.p.trailamount, 2)
                # p = self.data0.close[0]
                self.sell(size=self.p.stake,
                          exectype=bt.Order.StopTrailLimit,
                          price=p,
                          plimit=p + self.p.limitoffset,
                          valid=self.p.valid,
                          trailamount=self.p.trailamount,
                          trailpercent=self.p.trailpercent)


        # 如果持仓大于0,并没有不允许卖出平仓
        elif self.position.size > 0 and not self.p.donotsell and data.close[0] < sma[0] and data.close[-1] > sma[-1]:
            # 如果没有订单，市价单卖出仓位
            if self.order is None:
                self.order = self.sell(size=self.p.stake,
                                       exectype=bt.Order.Market,
                                       price=self.data0.close[0])
        # 如果当前存在订单，并且cancel设置大于0的时候，在next运行的次数大于self.cancel的时候，会触发取消订单
        elif self.order is not None and self.p.cancel:
            if self.datastatus > self.p.cancel:
                self.cancel(self.order)
        # 每个next，datastatus加1
        if self.datastatus:
            self.datastatus += 1

    def start(self):
        print("开始运行，获取时区")
        if self.data0.contractdetails is not None:
            print('Timezone from ContractDetails: {}'.format(
                self.data0.contractdetails.timeZoneId))
            print("Yutong Update --> Contract Details:", self.data0.contractdetails)

        header = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume',
                  'OpenInterest', 'SMA']
        print(', '.join(header))
        print(dir(self.data0.contractdetails))

        self.done = False


def runstrategy(args):
    # args = parse_args()

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
    print("Yutong Zhao Updating --> Data fetching parameters:", datakwargs)

    # 如果没有用store模式并且没有用设置broker，更新参数
    if not args.usestore and not args.broker:  # neither store nor broker
        datakwargs.update(storekwargs)  # pass the store args over the data
    # 获取数据
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
        "clientId": None,  # 默认情况下可以随机生成一个，开多个TWS的时候可以指定每个clientid，有一个master id 可以控制其他的clientid
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
        "smaperiod": 5,  # 策略运行使用的参数
        "replay": False,  # replay
        "resample": True,  # resample,和replay两个功能不能同时都设置成True
        "timeframe": bt.TimeFrame.Seconds,  # 交易的时间间隔
        "compression": 30,  # 多少个交易的时间间隔形成一个bar
        "timeframe1": bt.TimeFrame.Seconds,  # data1的
        "compression1": 5,  # data1的
        "no_takelate": False,  # 当latethrough设置成True的时候，resample或者replay形成新的bar的时候，是否使用来的比较迟的tick
        "no_bar2edge": False,  # no bar2edge for resample/replay
        "no_adjbartime": False,  # no adjbartime for resample/replay
        "no_rightedge": False,  # no rightedge for resample/replay
        "broker": True,  # 使用IB作为broker
        "trade": True,  # 是否进行买卖活动，设置成False的时候，不会进行买卖
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
    #args['data0'] = 'EUR.USD-CASH-IDEALPRO'
    args['data0'] = 'GOOG-STK-SMART-USD'
    new_args = AO(args)
    runstrategy(new_args)