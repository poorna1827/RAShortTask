from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from datetime import datetime
import time
import os
import csv


class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = []  # To store the received data

    def historicalData(self, reqId, bar):
        print(
            f"Date: {bar.date}, Open: {bar.open}, High: {bar.high}, Low: {bar.low}, Close: {bar.close}, Volume: {bar.volume}")
        self.data.append([bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume])

    def historicalDataEnd(self, reqId, start, end):
        print("Historical data fetch completed")
        self.disconnect()


def run_ib_api(ticker_list, start_date, end_date):
    output_folder = "C:/FinTech/mini_wt/yz_data/ibapi_daily"
    os.makedirs(output_folder, exist_ok=True)  # Ensure the directory exists

    for index, ticker in enumerate(ticker_list, start=1):
        app = IBapi()
        app.connect('127.0.0.1', 7497, 0)
        time.sleep(1)  # Allow time for connection to establish

        contract = Contract()
        contract.symbol = ticker
        contract.exchange = 'SMART'
        contract.currency = 'USD'
        contract.secType = 'STK'

        print(f"{index}. Fetching data for {ticker}")
        app.reqHistoricalData(reqId=index,
                              contract=contract,
                              endDateTime='',  # Fetch up to the most recent data
                              durationStr='20 Y',
                              barSizeSetting='1 day',
                              whatToShow='TRADES',  # Changed to 'TRADES'
                              useRTH=1,
                              formatDate=1,
                              keepUpToDate=False,
                              chartOptions=[])
        app.run()  # Fetch data

        # Write data to CSV
        csv_file_path = os.path.join(output_folder, f"{ticker}_daily_data_from_ibapi.csv")
        with open(csv_file_path, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['date', 'open', 'high', 'low', 'close', 'volume'])
            for data_point in app.data:
                csvwriter.writerow(data_point)

        app.data = []  # Clear data after writing to file
        app.disconnect()
        time.sleep(10)  # Sleep to avoid hitting rate limits

if __name__ == '__main__':
    with open('C:/FinTech/mini_wt/yz_data/sp_5_ticker_list.txt', 'r') as file:
        tickers = file.read().splitlines()

    start_date = '20000101 00:00:00 EST'
    end_date = '20240501 00:00:00 EST'

    run_ib_api(tickers, start_date, end_date)