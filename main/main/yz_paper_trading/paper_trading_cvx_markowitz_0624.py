#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import datetime
import time

import pytz
import numpy as np
import pandas as pd
from math import isclose
from datetime import datetime as dt
import mini_wt.main.backtrader as bt
from mini_wt.main.backtrader.utils import flushfile  # win32 quick stdout flushing
from mini_wt.main.backtrader.analyzers import PyFolio

class CVX_Markowitz_Strategy(bt.Strategy):
    params = (
        ('quantile_risk', 0.8),
        ('quantile_turn', 0.8),
        ('quantile_lev', 1),
        ('training', False),
    )

    def __init__(self):
        self.orderid = list()
        self.order = None
        self.counttostop = 0
        self.datastatus = 0
        self.position_dict = {}
        self.stock_dict = {}
        self.tickers = selected_stocks
        print('loading lru cache data')
        print('--------------------------------------------------')
        print('Strategy Created')
        print('--------------------------------------------------')

        self.target = 1/len(self.datas)

    def notify_data(self, data, status, *args, **kwargs):
        print(f'Data Status for {data._name} =>', data._getstatusname(status))
        if status == data.LIVE:
            self.datastatus = 1

    def notify_store(self, msg, *args, **kwargs):
        print('*' * 5, 'STORE NOTIF:', msg)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
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
            else:
                print(
                    "SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )
            self.bar_executed = len(self)
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
            print("Update --> Contract Details:", self.data0.contractdetails)
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

        now_cash = self.broker.getcash()
        now_value = self.broker.getvalue()

        self.curr_datetime = pd.to_datetime(self.datas[0].datetime.date(0))
        self.interest = 0.0003
        quantities = np.zeros(len(self.datas))
        w = np.zeros(len(self.datas))

        current_time = dt.now().astimezone(pytz.timezone('US/Eastern'))
        print("------------------------------------------------------------------")
        for data in self.datas:
            data_name = data._name
            eastern = pytz.timezone('US/Eastern')
            data_datetime = bt.num2date(data.datetime[0])
            if data_datetime.tzinfo is None or data_datetime.tzinfo.utcoffset(data_datetime) is None:
                data_datetime = eastern.localize(data_datetime.replace(tzinfo=None))
            else:
                data_datetime = data_datetime.astimezone(eastern)
            print(f"{data_name}, datetime: {data_datetime}, "
                  f" open: {data.open[0]}, high: {data.high[0]}, low: {data.low[0]},"
                  f" close: {data.close[0]}, volume: {data.volume[0]}, openinterest: {data.openinterest[0]},")
        print("------------------------------------------------------------------")

        for idx, data in enumerate(self.datas):
            data_date = data.datetime.date(0).strftime("%Y-%m-%d")
            if current_date == data_date:
                quantities[idx] = self.positionsbyname[data._name].size
                w[idx] = (quantities[idx] * self.positionsbyname[data._name].price) / now_value
            self.quantities_prev = quantities
            self.w_prev = w

        # if current_time.strftime("%H:%M") == "20:37":
        #     for idx, data in enumerate(self.datas):
        #         data_date = data.datetime.date(0).strftime("%Y-%m-%d")
        #         if current_date == data_date:
        #             if not isclose(self.target, self.w_prev[idx], abs_tol=1e-3):
        #                 self.order_target_percent(data, target=self.target)
        #
        # if current_time.strftime("%H:%M") == "20:37":
        #     for idx, data in enumerate(self.datas):
        #         data_date = data.datetime.date(0).strftime("%Y-%m-%d")
        #         if current_date == data_date:
        #             self.order_target_percent(data, target=0)

        if current_time.strftime("%H:%M") == "21:28":
            self.env.runstop()
            return

def runstrategy(ao, tickers):

    curr_date_ts = dt.now()

    curr_date = curr_date_ts.strftime('%Y-%m-%d')

    cerebro = bt.Cerebro()

    storekwargs = {
        'host': ao.host, 'port': ao.port,
        'clientId': ao.clientId, 'timeoffset': not ao.no_timeoffset,
        'reconnect': ao.reconnect, 'timeout': ao.timeout,
        'notifyall': ao.notifyall, '_debug': ao.debug
    }

    if ao.usestore:
        ibstore = bt.stores.IBStore(**storekwargs)

    if ao.broker:
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

    rekwargs = dict(
        timeframe=timeframe, compression=compression
    )

    for stock_symbol in tickers:
        if ao.usestore:
            datakwargs['dataname'] = stock_symbol
            data_feed = ibstore.getdata(**datakwargs)
            cerebro.resampledata(data_feed, **rekwargs)

    cerebro.addstrategy(CVX_Markowitz_Strategy)

    analyzers = [(PyFolio, {"_name": "pyfolio"})]

    for analyzer in analyzers:
        al = analyzer[0]
        alkwargs = analyzer[1]
        cerebro.addanalyzer(al, **alkwargs)

    cerebro.addwriter(bt.WriterFile, out=f"C:/FinTech/wt_data//trading_report/tradelog_{curr_date}.csv", csv=True)

    cerebro.run()

    analyzer_key = [analyzer[1]['_name'] for analyzer in analyzers]

    analyzer_stats = {key: getattr(cerebro.runstrats[0][0].analyzers, key) for key in analyzer_key}

    returns, positions, transactions, gross_lev = analyzer_stats['pyfolio'].get_pf_items()

    returns.index = returns.index.tz_localize(None)

    positions.index = positions.index.tz_localize(None)

    transactions.index = transactions.index.tz_localize(None)

    gross_lev.index = gross_lev.index.tz_localize(None)

    returns.to_csv("C:/FinTech/wt_data/trading_report/"+"returns.csv")

    positions.to_csv("C:/FinTech/wt_data/trading_report/"+"positions.csv")

    transactions.to_csv("C:/FinTech/wt_data/trading_report/"+"transactions.csv")

    gross_lev.to_csv("C:/FinTech/wt_data/trading_report/"+"gross_lev.csv")

args = {
    "exactbars": 0,
    "stopafter": 0,
    "plot": True,
    "usestore": True,
    "notifyall": False,
    "debug": False,
    "host": '127.0.0.1',
    "port": 7497,
    "qcheck": 0.5,
    "clientId": 95,
    "no_timeoffset": False,
    "reconnect": 3,
    "timeout": 3,
    "timezone": "US/Eastern",
    "what": None,
    "no_backfill_start": False,
    "latethrough": False,
    "no_backfill": False,
    "rtbar": False,
    "historical": False,
    "fromdate": False,
    "replay": False,
    "resample": True,
    "timeframe": bt.TimeFrame.Minutes,
    "compression": 1,
    "timeframe1": bt.TimeFrame.Seconds,
    "compression1": 5,
    "no_takelate": False,
    "no_bar2edge": False,
    "no_adjbartime": False,
    "no_rightedge": False,
    "broker": True,
    "trade": False,
    "donotsell": False,
    "exectype": bt.Order.Market,
    "stake": 1,
    "valid": None,
    "stoptrail": False,
    "traillimit": False,
    "oca": False,
    "bracket": False,
    "trailamount": None,
    "trailpercent": None,
    "limitoffset": None,
    "cancel": 0,
}

class AO():
    def __init__(self, args):
        for key, value in args.items():
            setattr(self, key, value)

if __name__ == '__main__':
    selected_stocks = pd.read_csv("C:/FinTech/wt_data/currency.txt", names=['tickers'], header=None)['tickers'].to_list()[0:45]

    tickers = [ticker + "-CASH-IDEALPRO" for ticker in selected_stocks]

    ao = AO(args)
    runstrategy(ao, tickers)