import yfinance as yf
import pandas as pd
from datetime import datetime
import os

def fetch_daily_stock_data(ticker_name, start_time, end_time):
    # Create a Ticker object
    stock = yf.Ticker(ticker_name)

    # Determine whether to use live or historical end time
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    if current_time < end_time:
        end_time = current_time  # Use the current time if it's before the specified end time

    try:
        # Get intraday data on a 1-minute interval for today
        hist = stock.history(period="1d", interval="1m")

        if hist.empty:
            print(f"No data found for {ticker_name}, possibly delisted.")
            return []

        # Filter data between start_time and end_time
        filtered_data = hist.between_time(start_time, end_time)

        if not filtered_data.empty:
            # Aggregate the data
            open_price = filtered_data.iloc[0]['Open']
            high_price = filtered_data['High'].max()
            low_price = filtered_data['Low'].min()
            close_price = filtered_data.iloc[-1]['Close']
            total_volume = filtered_data['Volume'].sum()
            # Assuming dividends and stock splits are reported once per day, not intraday
            dividends = hist['Dividends'].sum()
            stock_splits = hist['Stock Splits'].sum()

            # Return aggregated data as a list
            return [
                ticker_name, open_price, high_price, low_price,
                close_price, total_volume, dividends, stock_splits
            ]
    except Exception as e:
        print(f"Error processing {ticker_name}: {e}")
        return []

# Function to read stock symbols from a file and return current stock data for all
def fetch_all_current_stock_data(ticker_file_path, start_time, end_time):
    # Check if the file exists
    if not os.path.isfile(ticker_file_path):
        print("Ticker file path is not valid.")
        return []

    # Read the list of tickers from the file
    with open(ticker_file_path, 'r') as file:
        tickers = file.read().splitlines()

    # Container for all the stock data
    all_stock_data = []

    # Iterate over each ticker and fetch the data
    for ticker in tickers:
        stock_data = fetch_daily_stock_data(ticker, start_time, end_time)
        if stock_data:
            all_stock_data.append(stock_data)

    return all_stock_data

# Example usage
ticker_name = 'AAPL'  # Replace with your ticker
start_time = '09:30'
end_time = '15:45'
daily_stock_data = fetch_daily_stock_data(ticker_name, start_time, end_time)
print(daily_stock_data)

ticker_file_path = r'C:\Users\yutongzhao\Desktop\FinTechYuan\mini_wt\mini_wt\sp_500_ticker_list.txt'
current_stock_data = fetch_all_current_stock_data(ticker_file_path, start_time, end_time)
print(current_stock_data)  # This will contain the data for all tickers

